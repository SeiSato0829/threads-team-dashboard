const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs-extra');
const path = require('path');
const cron = require('node-cron');
const chokidar = require('chokidar');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const upload = multer({ dest: 'uploads/' });

// Enable CORS and JSON parsing
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Load settings
let settings = {};
try {
  const settingsPath = path.join(__dirname, 'settings.json');
  settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  console.log('✅ Settings loaded successfully');
} catch (error) {
  console.error('❌ Failed to load settings.json:', error.message);
  settings = {
    CLAUDE_API_KEY: '',
    BUFFER_ACCESS_TOKEN: '',
    BUFFER_PROFILE_ID: '',
    AUTO_POST_ENABLED: false,
    POST_INTERVAL_MINUTES: 60,
    DAILY_POST_LIMIT: 10
  };
}

// Initialize database
let db;
const initDatabase = () => {
  try {
    db = new sqlite3.Database('./threads_auto_post.db');
    
    // Create tables
    db.serialize(() => {
      // Posts table
      db.run(`CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        text TEXT NOT NULL,
        image_urls TEXT,
        genre TEXT,
        scheduled_time TEXT,
        buffer_sent_time TEXT,
        status TEXT DEFAULT 'pending',
        concept_source TEXT,
        reference_post TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`);
      
      // Company concepts table
      db.run(`CREATE TABLE IF NOT EXISTS company_concepts (
        id TEXT PRIMARY KEY,
        keywords TEXT NOT NULL,
        genre TEXT NOT NULL,
        reflection_status BOOLEAN DEFAULT FALSE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`);
      
      // Automation logs table
      db.run(`CREATE TABLE IF NOT EXISTS automation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT,
        data TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`);
    });
    
    console.log('✅ Database initialized successfully');
  } catch (error) {
    console.error('❌ Database initialization failed:', error.message);
  }
};

// Initialize Claude API (mock implementation)
const generateWithClaude = async (prompt, referenceData = []) => {
  // This would use the real Anthropic SDK in production
  if (!settings.CLAUDE_API_KEY || settings.CLAUDE_API_KEY.includes('your-claude-api-key')) {
    // Mock response for demo
    return {
      improved_text: `AI改良版: ${prompt}\n\n#人気投稿をもとにAIが改良しました #Threads #SNS`,
      confidence: 0.85,
      suggestions: ['ハッシュタグを追加', '絵文字を使用', '改行で読みやすく'],
      mock: true
    };
  }
  
  try {
    // Real Claude API implementation would go here
    // const anthropic = new Anthropic({ apiKey: settings.CLAUDE_API_KEY });
    // const message = await anthropic.messages.create({ ... });
    
    return {
      improved_text: `AI改良版: ${prompt}`,
      confidence: 0.90,
      mock: false
    };
  } catch (error) {
    console.error('Claude API Error:', error);
    throw error;
  }
};

// Initialize Buffer API (mock implementation)
const scheduleWithBuffer = async (text, scheduledTime, imageUrls = []) => {
  if (!settings.BUFFER_ACCESS_TOKEN || settings.BUFFER_ACCESS_TOKEN.includes('your-buffer-token')) {
    // Mock response for demo
    return {
      success: true,
      buffer_id: `mock_${Date.now()}`,
      scheduled_at: scheduledTime,
      mock: true
    };
  }
  
  try {
    // Real Buffer API implementation would go here
    const bufferUrl = 'https://api.bufferapp.com/1/updates/create.json';
    // const response = await fetch(bufferUrl, { ... });
    
    return {
      success: true,
      buffer_id: `buffer_${Date.now()}`,
      scheduled_at: scheduledTime,
      mock: false
    };
  } catch (error) {
    console.error('Buffer API Error:', error);
    throw error;
  }
};

// Automation state
let automationState = {
  isRunning: false,
  lastProcessed: null,
  todayPosts: 0,
  queuedPosts: 0,
  nextScheduled: null,
  csvWatcher: null,
  scrapingScheduler: null,
  lastScraping: null,
  nextScraping: null
};

// CSV file watcher
const startCSVWatcher = () => {
  const csvFolder = settings.CSV_WATCH_FOLDER || './csv_input';
  
  // Ensure folder exists
  fs.ensureDirSync(csvFolder);
  
  if (automationState.csvWatcher) {
    automationState.csvWatcher.close();
  }
  
  automationState.csvWatcher = chokidar.watch(path.join(csvFolder, '*.csv'), {
    ignoreInitial: false,
    persistent: true
  });
  
  automationState.csvWatcher.on('add', async (filePath) => {
    console.log(`📊 New CSV file detected: ${filePath}`);
    await processCSVFile(filePath);
  });
  
  console.log(`👀 CSV watcher started for folder: ${csvFolder}`);
};

// Process CSV file automatically
const processCSVFile = async (filePath) => {
  try {
    const csvContent = fs.readFileSync(filePath, 'utf8');
    const lines = csvContent.split('\\n');
    const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
    
    const csvData = lines.slice(1)
      .filter(line => line.trim())
      .map(line => {
        const values = line.split(',').map(v => v.replace(/"/g, '').trim());
        return {
          postText: values[0] || '',
          imageUrl: values[1] || '',
          likes: parseInt(values[2]) || 0,
          genre: values[3] || ''
        };
      })
      .sort((a, b) => b.likes - a.likes)
      .slice(0, 10); // Top 10
    
    // Generate AI posts for each CSV entry
    const generatedPosts = [];
    for (const item of csvData) {
      try {
        const aiResult = await generateWithClaude(item.postText, csvData);
        
        const newPost = {
          id: `auto-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          text: aiResult.improved_text,
          imageUrls: item.imageUrl ? [item.imageUrl] : [],
          genre: item.genre || 'auto',
          scheduledTime: new Date(Date.now() + (generatedPosts.length + 1) * settings.POST_INTERVAL_MINUTES * 60 * 1000).toISOString(),
          status: 'pending',
          referencePost: item.postText,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
        
        generatedPosts.push(newPost);
      } catch (error) {
        console.error('Error generating post:', error);
      }
    }
    
    // Save to database
    if (generatedPosts.length > 0) {
      savePostsToDatabase(generatedPosts);
      automationState.queuedPosts += generatedPosts.length;
      
      // Log automation activity
      logAutomationActivity('csv_processed', 'success', `Generated ${generatedPosts.length} posts from ${path.basename(filePath)}`);
    }
    
    // Move processed file to archive
    const archiveFolder = path.join(path.dirname(filePath), 'processed');
    fs.ensureDirSync(archiveFolder);
    const archivePath = path.join(archiveFolder, `${Date.now()}_${path.basename(filePath)}`);
    fs.moveSync(filePath, archivePath);
    
    console.log(`✅ Processed CSV file: ${generatedPosts.length} posts generated`);
    
  } catch (error) {
    console.error('❌ CSV processing error:', error);
    logAutomationActivity('csv_processed', 'error', error.message);
  }
};

// Save posts to database
const savePostsToDatabase = (posts) => {
  const stmt = db.prepare(`
    INSERT INTO posts (id, text, image_urls, genre, scheduled_time, status, reference_post, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  posts.forEach(post => {
    stmt.run([
      post.id,
      post.text,
      JSON.stringify(post.imageUrls),
      post.genre,
      post.scheduledTime,
      post.status,
      post.referencePost,
      post.createdAt,
      post.updatedAt
    ]);
  });
  
  stmt.finalize();
};

// Log automation activity
const logAutomationActivity = (action, status, message, data = null) => {
  const stmt = db.prepare(`
    INSERT INTO automation_logs (action, status, message, data)
    VALUES (?, ?, ?, ?)
  `);
  
  stmt.run([action, status, message, data ? JSON.stringify(data) : null]);
  stmt.finalize();
};

// Schedule posts automatically
const scheduleAutoPosts = () => {
  if (!automationState.isRunning) return;
  
  db.all(`
    SELECT * FROM posts 
    WHERE status = 'pending' 
    AND scheduled_time <= datetime('now', '+15 minutes')
    ORDER BY scheduled_time ASC
    LIMIT 5
  `, async (err, rows) => {
    if (err) {
      console.error('Database error:', err);
      return;
    }
    
    for (const post of rows) {
      try {
        // Schedule with Buffer
        const bufferResult = await scheduleWithBuffer(
          post.text,
          post.scheduled_time,
          JSON.parse(post.image_urls || '[]')
        );
        
        if (bufferResult.success) {
          // Update post status
          db.run(`
            UPDATE posts 
            SET status = 'scheduled', buffer_sent_time = ?, updated_at = ?
            WHERE id = ?
          `, [new Date().toISOString(), new Date().toISOString(), post.id]);
          
          automationState.todayPosts++;
          automationState.queuedPosts--;
          
          console.log(`📤 Scheduled post: ${post.id}`);
          logAutomationActivity('post_scheduled', 'success', `Scheduled post ${post.id}`);
        }
      } catch (error) {
        console.error('Scheduling error:', error);
        db.run(`UPDATE posts SET status = 'failed' WHERE id = ?`, [post.id]);
        logAutomationActivity('post_scheduled', 'error', `Failed to schedule ${post.id}: ${error.message}`);
      }
    }
  });
};

// Easy Scraper automatic execution
const runEasyScraper = async (scrapingTargets = []) => {
  try {
    logAutomationActivity('scraping_started', 'info', 'Starting Easy Scraper execution');
    
    // Default scraping targets if none provided
    const defaultTargets = [
      { platform: 'threads', keywords: ['ゲーム', 'エンタメ'], limit: 50 },
      { platform: 'twitter', keywords: ['ビジネス', 'マーケティング'], limit: 30 },
      { platform: 'instagram', keywords: ['ライフスタイル', 'グルメ'], limit: 40 }
    ];
    
    const targets = scrapingTargets.length > 0 ? scrapingTargets : defaultTargets;
    let totalScraped = 0;
    
    for (const target of targets) {
      try {
        // Simulate Easy Scraper execution (in real implementation, this would call Easy Scraper CLI/API)
        const scrapedData = await simulateEasyScraper(target);
        
        if (scrapedData.length > 0) {
          // Save scraped data as CSV
          const csvContent = generateCSVContent(scrapedData);
          const fileName = `auto_scraped_${target.platform}_${Date.now()}.csv`;
          const filePath = path.join(settings.CSV_WATCH_FOLDER || './csv_input', fileName);
          
          await fs.writeFile(filePath, csvContent, 'utf8');
          totalScraped += scrapedData.length;
          
          console.log(`📊 Scraped ${scrapedData.length} posts from ${target.platform} → ${fileName}`);
        }
      } catch (error) {
        console.error(`❌ Scraping failed for ${target.platform}:`, error.message);
        logAutomationActivity('scraping_error', 'error', `Failed to scrape ${target.platform}: ${error.message}`);
      }
    }
    
    automationState.lastScraping = new Date().toISOString();
    
    // Calculate next scraping time
    const nextTime = new Date();
    nextTime.setHours(nextTime.getHours() + (settings.SCRAPING_INTERVAL_HOURS || 8));
    automationState.nextScraping = nextTime.toISOString();
    
    logAutomationActivity('scraping_completed', 'success', `Scraped ${totalScraped} total posts`);
    
    return {
      success: true,
      totalScraped,
      targets: targets.length,
      nextScraping: automationState.nextScraping
    };
    
  } catch (error) {
    console.error('❌ Easy Scraper execution failed:', error);
    logAutomationActivity('scraping_failed', 'error', error.message);
    throw error;
  }
};

// Simulate Easy Scraper (replace with actual Easy Scraper integration)
const simulateEasyScraper = async (target) => {
  // In real implementation, this would execute Easy Scraper with specific parameters
  // For now, we'll generate realistic mock data
  
  const mockPosts = [];
  const postCount = Math.min(target.limit, Math.floor(Math.random() * 20) + 10);
  
  for (let i = 0; i < postCount; i++) {
    const likes = Math.floor(Math.random() * 1000) + 50;
    const keyword = target.keywords[Math.floor(Math.random() * target.keywords.length)];
    
    mockPosts.push({
      postText: `${keyword}に関する投稿 #${i + 1} - ${target.platform}から取得`,
      imageUrl: `https://example.com/${target.platform}_image_${i}.jpg`,
      likes: likes,
      genre: keyword,
      platform: target.platform,
      scraped_at: new Date().toISOString()
    });
  }
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return mockPosts;
};

// Generate CSV content from scraped data
const generateCSVContent = (data) => {
  const headers = ['投稿文', '画像URL', 'いいね数', 'ジャンル'];
  const rows = data.map(item => [
    `"${item.postText}"`,
    `"${item.imageUrl}"`,
    item.likes,
    `"${item.genre}"`
  ]);
  
  return [headers.join(','), ...rows.map(row => row.join(','))].join('\\n');
};

// Start scraping scheduler
const startScrapingScheduler = () => {
  if (automationState.scrapingScheduler) {
    automationState.scrapingScheduler.destroy();
  }
  
  // Schedule scraping every 8 hours (or configured interval)
  const interval = settings.SCRAPING_INTERVAL_HOURS || 8;
  const cronPattern = `0 */${interval} * * *`; // Every X hours
  
  automationState.scrapingScheduler = cron.schedule(cronPattern, async () => {
    if (automationState.isRunning) {
      console.log('🕷️ Starting scheduled scraping...');
      try {
        await runEasyScraper();
      } catch (error) {
        console.error('Scheduled scraping failed:', error);
      }
    }
  });
  
  // Set next scraping time
  const nextTime = new Date();
  nextTime.setHours(nextTime.getHours() + interval);
  automationState.nextScraping = nextTime.toISOString();
  
  console.log(`🕷️ Scraping scheduler started: every ${interval} hours`);
};

// ===================
// API ENDPOINTS
// ===================

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    message: 'Complete Threads Auto Post System',
    version: 'v3.2-complete',
    timestamp: new Date().toISOString(),
    automation_running: automationState.isRunning
  });
});

// Get all posts
app.get('/api/posts', (req, res) => {
  db.all(`
    SELECT * FROM posts 
    ORDER BY created_at DESC
  `, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    const posts = rows.map(row => ({
      ...row,
      imageUrls: JSON.parse(row.image_urls || '[]'),
      scheduledTime: row.scheduled_time,
      createdAt: row.created_at,
      updatedAt: row.updated_at
    }));
    
    res.json({
      posts,
      total: posts.length
    });
  });
});

// Save posts
app.post('/api/posts', (req, res) => {
  const posts = Array.isArray(req.body) ? req.body : [req.body];
  
  try {
    savePostsToDatabase(posts);
    res.json({
      success: true,
      saved_count: posts.length,
      message: 'Posts saved successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// CSV processing
app.post('/api/csv/process', async (req, res) => {
  try {
    const { csv_data } = req.body;
    
    const processedPosts = csv_data.slice(0, 10).map((item, index) => ({
      id: `csv-${Date.now()}-${index}`,
      text: `AI改良版: ${item.postText}\\n\\n#${item.genre} #人気投稿をもとにAIが改良しました`,
      imageUrls: item.imageUrl ? [item.imageUrl] : [],
      genre: item.genre || 'general',
      scheduledTime: new Date(Date.now() + (index + 1) * 60 * 60 * 1000).toISOString(),
      status: 'pending',
      referencePost: item.postText,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }));

    res.json({
      success: true,
      posts: processedPosts,
      processed_count: processedPosts.length,
      message: 'CSV processed successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// AI generation
app.post('/api/ai/generate', async (req, res) => {
  try {
    const { text, genre, reference_posts } = req.body;
    const result = await generateWithClaude(text, reference_posts);
    
    res.json({
      success: true,
      improved_text: result.improved_text,
      confidence: result.confidence,
      mock: result.mock || false
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Image upload
app.post('/api/upload/image', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({
      success: false,
      message: 'No image file provided'
    });
  }

  const imageUrl = `http://localhost:5000/images/${req.file.filename}`;
  
  res.json({
    success: true,
    url: imageUrl,
    filename: req.file.filename
  });
});

// Schedule post
app.post('/api/schedule', async (req, res) => {
  try {
    const { text, scheduled_time, image_urls } = req.body;
    const result = await scheduleWithBuffer(text, scheduled_time, image_urls);
    
    res.json({
      success: true,
      buffer_send_time: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      schedule_id: result.buffer_id,
      mock: result.mock || false
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Automation settings
app.get('/api/automation/settings', (req, res) => {
  res.json({
    success: true,
    settings: {
      enabled: settings.AUTO_POST_ENABLED,
      csvWatchFolder: settings.CSV_WATCH_FOLDER || './csv_input',
      postInterval: settings.POST_INTERVAL_MINUTES || 60,
      dailyPostLimit: settings.DAILY_POST_LIMIT || 10,
      postTimeStart: settings.POST_TIME_START || '09:00',
      postTimeEnd: settings.POST_TIME_END || '21:00',
      autoGenerate: true,
      bufferSchedule: true
    }
  });
});

app.post('/api/automation/settings', (req, res) => {
  try {
    // Update settings
    Object.assign(settings, req.body);
    
    // Save to file
    fs.writeFileSync('./settings.json', JSON.stringify(settings, null, 2));
    
    res.json({
      success: true,
      message: 'Automation settings saved successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Automation status
app.get('/api/automation/status', (req, res) => {
  // Calculate next scheduled time
  let nextScheduled = null;
  if (automationState.isRunning) {
    nextScheduled = new Date(Date.now() + settings.POST_INTERVAL_MINUTES * 60 * 1000).toISOString();
  }
  
  res.json({
    success: true,
    status: {
      isRunning: automationState.isRunning,
      lastProcessed: automationState.lastProcessed,
      todayPosts: automationState.todayPosts,
      queuedPosts: automationState.queuedPosts,
      nextScheduled,
      lastScraping: automationState.lastScraping,
      nextScraping: automationState.nextScraping
    }
  });
});

// Start automation
app.post('/api/automation/start', (req, res) => {
  try {
    automationState.isRunning = true;
    
    // Start CSV watcher
    startCSVWatcher();
    
    // Start scraping scheduler
    startScrapingScheduler();
    
    // Schedule periodic checks
    if (!automationState.cronJob) {
      automationState.cronJob = cron.schedule('*/5 * * * *', () => {
        scheduleAutoPosts();
      });
    }
    
    logAutomationActivity('automation_started', 'success', 'Automation system started');
    
    res.json({
      success: true,
      message: '🤖 自動投稿システムを開始しました！CSV監視とスケジュール投稿が有効になります。'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Stop automation
app.post('/api/automation/stop', (req, res) => {
  try {
    automationState.isRunning = false;
    
    // Stop CSV watcher
    if (automationState.csvWatcher) {
      automationState.csvWatcher.close();
      automationState.csvWatcher = null;
    }
    
    // Stop scraping scheduler
    if (automationState.scrapingScheduler) {
      automationState.scrapingScheduler.destroy();
      automationState.scrapingScheduler = null;
    }
    
    // Stop cron job
    if (automationState.cronJob) {
      automationState.cronJob.destroy();
      automationState.cronJob = null;
    }
    
    logAutomationActivity('automation_stopped', 'success', 'Automation system stopped');
    
    res.json({
      success: true,
      message: '🛑 自動投稿システムを停止しました。'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Manual scraping trigger
app.post('/api/scraping/run', async (req, res) => {
  try {
    const { targets } = req.body;
    const result = await runEasyScraper(targets);
    
    res.json({
      success: true,
      message: `🕷️ スクレイピングを実行しました！${result.totalScraped}件のデータを取得`,
      ...result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get scraping logs
app.get('/api/scraping/logs', (req, res) => {
  db.all(`
    SELECT * FROM automation_logs 
    WHERE action LIKE '%scraping%' 
    ORDER BY created_at DESC 
    LIMIT 50
  `, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    res.json({
      success: true,
      logs: rows
    });
  });
});

// Serve uploaded images
app.use('/images', express.static('uploads'));

// Initialize and start server
const startServer = async () => {
  // Ensure required directories exist
  await fs.ensureDir('./uploads');
  await fs.ensureDir('./csv_input');
  
  // Initialize database
  initDatabase();
  
  // Start server
  app.listen(PORT, () => {
    console.log(`🚀 Complete Threads Auto Post Server running on http://localhost:${PORT}`);
    console.log(`📊 CSV Watch Folder: ${settings.CSV_WATCH_FOLDER || './csv_input'}`);
    console.log(`🤖 AI Model: ${settings.AI_MODEL || 'claude-3-haiku-20240307'}`);
    console.log(`⚙️  Check settings.json for API configuration`);
  });
};

startServer().catch(console.error);