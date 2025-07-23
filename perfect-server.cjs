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
    DAILY_POST_LIMIT: 10,
    SCRAPING_INTERVAL_HOURS: 8,
    SCRAPING_ENABLED: true
  };
}

// Initialize database
let db;
const initDatabase = () => {
  try {
    // Delete old database for clean start
    if (fs.existsSync('./threads_auto_post.db')) {
      console.log('🗑️ Removing old database for fresh start...');
      fs.unlinkSync('./threads_auto_post.db');
    }
    
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
      
      // Processed files table
      db.run(`CREATE TABLE IF NOT EXISTS processed_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE NOT NULL,
        processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        posts_generated INTEGER DEFAULT 0
      )`);
    });
    
    console.log('✅ Database initialized successfully');
  } catch (error) {
    console.error('❌ Database initialization failed:', error.message);
  }
};

// Check if file was already processed
const isFileProcessed = (filename) => {
  return new Promise((resolve, reject) => {
    db.get('SELECT * FROM processed_files WHERE filename = ?', [filename], (err, row) => {
      if (err) reject(err);
      else resolve(!!row);
    });
  });
};

// Mark file as processed
const markFileAsProcessed = (filename, postsGenerated) => {
  return new Promise((resolve, reject) => {
    db.run('INSERT INTO processed_files (filename, posts_generated) VALUES (?, ?)', 
      [filename, postsGenerated], 
      function(err) {
        if (err) reject(err);
        else resolve(this.lastID);
      }
    );
  });
};

// Initialize Claude API (enhanced mock implementation)
const generateWithClaude = async (prompt, referenceData = []) => {
  // This would use the real Anthropic SDK in production
  if (!settings.CLAUDE_API_KEY || settings.CLAUDE_API_KEY.includes('your-claude-api-key')) {
    // Enhanced mock responses
    const templates = [
      {
        text: `🎮 ${prompt}\n\n今話題のゲーム情報をお届け！みんなもチェックしてみて！\n\n#ゲーム #Gaming #Threads #トレンド`,
        tags: ['ゲーム', 'Gaming', 'Threads', 'トレンド']
      },
      {
        text: `✨ ${prompt}\n\nエンタメ業界の最新トレンドをチェック！フォロー&シェアお願いします！\n\n#エンタメ #Entertainment #話題 #最新情報`,
        tags: ['エンタメ', 'Entertainment', '話題', '最新情報']
      },
      {
        text: `🚀 ${prompt}\n\n知らなきゃ損する最新情報！保存して後でチェック！\n\n#トレンド #最新情報 #必見 #バズり`,
        tags: ['トレンド', '最新情報', '必見', 'バズり']
      },
      {
        text: `💡 ${prompt}\n\nこれは見逃せない話題です！いいねとコメントお待ちしてます！\n\n#注目 #シェア拡散希望 #最新 #フォロー`,
        tags: ['注目', 'シェア拡散希望', '最新', 'フォロー']
      },
      {
        text: `🔥 ${prompt}\n\nSNSで話題沸騰中！あなたの意見も聞かせて！\n\n#バズり #拡散希望 #トレンド #コメント歓迎`,
        tags: ['バズり', '拡散希望', 'トレンド', 'コメント歓迎']
      }
    ];
    
    const selected = templates[Math.floor(Math.random() * templates.length)];
    
    return {
      improved_text: selected.text,
      confidence: 0.85 + Math.random() * 0.15,
      suggestions: ['ハッシュタグを追加', '絵文字を使用', '改行で読みやすく', 'CTAを追加'],
      tags: selected.tags,
      mock: true
    };
  }
  
  try {
    // Real Claude API implementation would go here
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
  postScheduler: null,
  lastScraping: null,
  nextScraping: null,
  processedFiles: new Set()
};

// Parse CSV content - FIXED for literal \n
const parseCSVContent = (content) => {
  try {
    console.log('📋 Raw CSV content length:', content.length);
    console.log('📋 First 200 chars:', content.substring(0, 200));
    
    // Replace literal \n with actual newlines
    const fixedContent = content.replace(/\\n/g, '\n').replace(/\\r/g, '\r');
    
    // Split by actual newlines
    const lines = fixedContent.split(/\r?\n/).filter(line => line.trim());
    console.log(`📋 Found ${lines.length} lines in CSV`);
    
    if (lines.length < 2) {
      console.log('❌ Not enough lines in CSV');
      return [];
    }
    
    // Parse headers
    const headers = lines[0].split(',').map(h => h.replace(/^"|"$/g, '').trim());
    console.log('📋 Headers:', headers);
    
    // Parse data rows
    const data = [];
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim()) continue;
      
      // Handle quoted values properly
      const values = [];
      let current = '';
      let inQuotes = false;
      
      for (let j = 0; j < line.length; j++) {
        const char = line[j];
        
        if (char === '"' && (j === 0 || line[j-1] === ',')) {
          inQuotes = true;
        } else if (char === '"' && inQuotes && (j === line.length - 1 || line[j+1] === ',')) {
          inQuotes = false;
        } else if (char === ',' && !inQuotes) {
          values.push(current.trim());
          current = '';
        } else {
          current += char;
        }
      }
      values.push(current.trim());
      
      // Create object from values
      const obj = {};
      headers.forEach((header, index) => {
        obj[header] = values[index] || '';
      });
      
      data.push(obj);
    }
    
    console.log(`📋 Parsed ${data.length} data rows`);
    return data;
    
  } catch (error) {
    console.error('❌ CSV parsing error:', error);
    return [];
  }
};

// Process CSV file automatically
const processCSVFile = async (filePath, skipDuplicateCheck = false) => {
  try {
    const filename = path.basename(filePath);
    console.log(`\n🔄 Starting to process: ${filename}`);
    
    // Check if already processed
    if (!skipDuplicateCheck) {
      const alreadyProcessed = await isFileProcessed(filename);
      if (alreadyProcessed) {
        console.log(`✓ File already processed: ${filename}`);
        return;
      }
    }
    
    // Read file content
    const csvContent = await fs.readFile(filePath, 'utf8');
    console.log(`📄 Read ${csvContent.length} bytes from ${filename}`);
    
    // Parse CSV data
    const records = parseCSVContent(csvContent);
    console.log(`📊 Parsed ${records.length} records from CSV`);
    
    if (records.length === 0) {
      console.log('❌ No valid records found in CSV');
      return;
    }
    
    // Show sample record
    console.log('📋 Sample record:', records[0]);
    
    // Map to expected format
    const csvData = records.map(record => ({
      postText: record['投稿文'] || record.postText || record.text || '',
      imageUrl: record['画像URL'] || record.imageUrl || record.image || '',
      likes: parseInt(record['いいね数'] || record.likes || '0') || 0,
      genre: record['ジャンル'] || record.genre || record.category || 'general'
    }))
    .filter(item => item.postText && item.postText.trim()) // Only process items with text
    .sort((a, b) => b.likes - a.likes) // Sort by likes
    .slice(0, 10); // Top 10
    
    console.log(`🎯 Processing top ${csvData.length} posts from ${filename}`);
    
    if (csvData.length === 0) {
      console.log('❌ No valid posts after filtering');
      return;
    }
    
    // Generate AI posts for each CSV entry
    const generatedPosts = [];
    let successCount = 0;
    
    for (let i = 0; i < csvData.length; i++) {
      const item = csvData[i];
      try {
        console.log(`🤖 Generating AI post ${i + 1}/${csvData.length} for: "${item.postText.substring(0, 50)}..."`);
        const aiResult = await generateWithClaude(item.postText, csvData);
        
        const scheduledDate = new Date();
        scheduledDate.setMinutes(scheduledDate.getMinutes() + (generatedPosts.length + automationState.queuedPosts + 1) * settings.POST_INTERVAL_MINUTES);
        
        const newPost = {
          id: `auto-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          text: aiResult.improved_text,
          imageUrls: item.imageUrl ? [item.imageUrl] : [],
          genre: item.genre || 'auto',
          scheduledTime: scheduledDate.toISOString(),
          status: 'pending',
          conceptSource: 'csv_import',
          referencePost: item.postText,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
        
        generatedPosts.push(newPost);
        successCount++;
        console.log(`✅ Generated post ${successCount}: ${newPost.id}`);
        
        // Small delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 50));
      } catch (error) {
        console.error(`❌ Error generating post ${i + 1}:`, error.message);
      }
    }
    
    // Save to database
    if (generatedPosts.length > 0) {
      console.log(`💾 Saving ${generatedPosts.length} posts to database...`);
      const savedCount = await savePostsToDatabase(generatedPosts);
      
      automationState.queuedPosts += savedCount;
      automationState.lastProcessed = new Date().toISOString();
      
      // Update next scheduled time
      if (generatedPosts.length > 0) {
        automationState.nextScheduled = generatedPosts[0].scheduledTime;
      }
      
      // Mark file as processed
      await markFileAsProcessed(filename, savedCount);
      
      // Log automation activity
      logAutomationActivity('csv_processed', 'success', 
        `Generated ${savedCount} posts from ${filename}`, 
        { filename, postsGenerated: savedCount }
      );
      
      console.log(`✅ Successfully processed ${filename}: ${savedCount} posts saved to database`);
    }
    
    // Move processed file to archive
    const archiveFolder = path.join(path.dirname(filePath), 'processed');
    await fs.ensureDir(archiveFolder);
    const archivePath = path.join(archiveFolder, `${Date.now()}_${filename}`);
    
    try {
      await fs.move(filePath, archivePath);
      console.log(`📁 Moved to archive: ${path.basename(archivePath)}`);
    } catch (moveError) {
      console.error('❌ Failed to move file to archive:', moveError.message);
      // Don't fail the whole process if we can't move the file
    }
    
  } catch (error) {
    console.error('❌ CSV processing error:', error);
    console.error(error.stack);
    logAutomationActivity('csv_processed', 'error', error.message, { filename: path.basename(filePath) });
  }
};

// Save posts to database (improved with better error handling)
const savePostsToDatabase = async (posts) => {
  return new Promise((resolve, reject) => {
    let savedCount = 0;
    const errors = [];
    
    db.serialize(() => {
      const stmt = db.prepare(`
        INSERT INTO posts (id, text, image_urls, genre, scheduled_time, status, concept_source, reference_post, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);
      
      posts.forEach((post, index) => {
        stmt.run([
          post.id,
          post.text,
          JSON.stringify(post.imageUrls || []),
          post.genre,
          post.scheduledTime,
          post.status || 'pending',
          post.conceptSource || 'csv_import',
          post.referencePost || '',
          post.createdAt,
          post.updatedAt
        ], function(err) {
          if (err) {
            console.error(`❌ Error saving post ${index + 1}:`, err.message);
            errors.push({ index, error: err.message });
          } else {
            savedCount++;
            console.log(`💾 Saved post ${savedCount}/${posts.length}`);
          }
        });
      });
      
      stmt.finalize(() => {
        console.log(`✅ Database operation complete: ${savedCount}/${posts.length} posts saved`);
        if (errors.length > 0) {
          console.error(`⚠️ ${errors.length} errors occurred during save`);
        }
        resolve(savedCount);
      });
    });
  });
};

// Process existing CSV files on startup
const processExistingCSVFiles = async () => {
  const csvFolder = settings.CSV_WATCH_FOLDER || './csv_input';
  
  try {
    const files = await fs.readdir(csvFolder);
    const csvFiles = files.filter(file => file.endsWith('.csv'));
    
    console.log(`\n📊 Found ${csvFiles.length} CSV files to process`);
    
    let totalProcessed = 0;
    for (const file of csvFiles) {
      const filePath = path.join(csvFolder, file);
      console.log(`\n📄 Processing file ${totalProcessed + 1}/${csvFiles.length}: ${file}`);
      
      await processCSVFile(filePath, false);
      totalProcessed++;
      
      // Small delay between files
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    console.log(`\n✅ Finished processing ${totalProcessed} CSV files`);
    
    // Update queue count after processing
    await updateQueueCount();
    
  } catch (error) {
    console.error('❌ Error processing existing CSV files:', error);
  }
};

// CSV file watcher
const startCSVWatcher = async () => {
  const csvFolder = settings.CSV_WATCH_FOLDER || './csv_input';
  
  // Ensure folder exists
  await fs.ensureDir(csvFolder);
  
  // Process existing files first
  await processExistingCSVFiles();
  
  if (automationState.csvWatcher) {
    automationState.csvWatcher.close();
  }
  
  automationState.csvWatcher = chokidar.watch(path.join(csvFolder, '*.csv'), {
    ignoreInitial: true, // We already processed existing files
    persistent: true,
    awaitWriteFinish: {
      stabilityThreshold: 2000,
      pollInterval: 100
    }
  });
  
  automationState.csvWatcher.on('add', async (filePath) => {
    console.log(`\n📊 New CSV file detected: ${path.basename(filePath)}`);
    await processCSVFile(filePath);
    await updateQueueCount();
  });
  
  automationState.csvWatcher.on('error', error => {
    console.error('❌ Watcher error:', error);
  });
  
  console.log(`\n👀 CSV watcher started for folder: ${csvFolder}`);
};

// Log automation activity
const logAutomationActivity = (action, status, message, data = null) => {
  db.run(`
    INSERT INTO automation_logs (action, status, message, data)
    VALUES (?, ?, ?, ?)
  `, [action, status, message, data ? JSON.stringify(data) : null], (err) => {
    if (err) console.error('Log error:', err);
  });
};

// Schedule posts automatically
const scheduleAutoPosts = async () => {
  if (!automationState.isRunning) return;
  
  const now = new Date();
  const startHour = parseInt(settings.POST_TIME_START?.split(':')[0] || 9);
  const endHour = parseInt(settings.POST_TIME_END?.split(':')[0] || 21);
  const currentHour = now.getHours();
  
  // Check if within posting hours
  if (currentHour < startHour || currentHour >= endHour) {
    console.log(`⏰ Outside posting hours (${startHour}:00 - ${endHour}:00)`);
    return;
  }
  
  // Check daily limit
  if (automationState.todayPosts >= (settings.DAILY_POST_LIMIT || 10)) {
    console.log(`📊 Daily limit reached (${automationState.todayPosts}/${settings.DAILY_POST_LIMIT})`);
    return;
  }
  
  db.all(`
    SELECT * FROM posts 
    WHERE status = 'pending' 
    AND scheduled_time <= datetime('now', '+15 minutes')
    ORDER BY scheduled_time ASC
    LIMIT 5
  `, async (err, rows) => {
    if (err) {
      console.error('❌ Database error:', err);
      return;
    }
    
    if (rows.length === 0) {
      return;
    }
    
    console.log(`\n📤 Found ${rows.length} posts ready to schedule`);
    
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
          `, [new Date().toISOString(), new Date().toISOString(), post.id], (err) => {
            if (!err) {
              automationState.todayPosts++;
              automationState.queuedPosts = Math.max(0, automationState.queuedPosts - 1);
              console.log(`✅ Scheduled post: ${post.id} (Today: ${automationState.todayPosts})`);
              logAutomationActivity('post_scheduled', 'success', `Scheduled post ${post.id}`);
            }
          });
        }
      } catch (error) {
        console.error('❌ Scheduling error:', error);
        db.run(`UPDATE posts SET status = 'failed' WHERE id = ?`, [post.id]);
        logAutomationActivity('post_scheduled', 'error', `Failed to schedule ${post.id}: ${error.message}`);
      }
    }
    
    // Update next scheduled time
    db.get(`
      SELECT MIN(scheduled_time) as next_time 
      FROM posts 
      WHERE status = 'pending'
    `, (err, row) => {
      if (!err && row && row.next_time) {
        automationState.nextScheduled = row.next_time;
      }
    });
  });
};

// Reset daily counter
const resetDailyCounter = () => {
  automationState.todayPosts = 0;
  console.log('📅 Daily post counter reset');
  logAutomationActivity('daily_reset', 'success', 'Daily counter reset');
};

// Easy Scraper automatic execution
const runEasyScraper = async (scrapingTargets = []) => {
  try {
    console.log('\n🕷️ Starting Easy Scraper execution...');
    logAutomationActivity('scraping_started', 'info', 'Starting Easy Scraper execution');
    
    // Use settings targets if none provided
    const targets = scrapingTargets.length > 0 ? scrapingTargets : (settings.SCRAPING_TARGETS || [
      { platform: 'threads', keywords: ['ゲーム', 'エンタメ'], limit: 50 },
      { platform: 'twitter', keywords: ['ビジネス', 'マーケティング'], limit: 30 },
      { platform: 'instagram', keywords: ['ライフスタイル', 'グルメ'], limit: 40 }
    ]);
    
    let totalScraped = 0;
    
    for (const target of targets) {
      try {
        console.log(`🕷️ Scraping ${target.platform} for keywords: ${target.keywords.join(', ')}`);
        const scrapedData = await simulateEasyScraper(target);
        
        if (scrapedData.length > 0) {
          // Save scraped data as CSV with proper format
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
    console.log(`✅ Scraping completed: ${totalScraped} total posts collected`);
    
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

// Simulate Easy Scraper (realistic mock data)
const simulateEasyScraper = async (target) => {
  const mockPosts = [];
  const postCount = Math.min(target.limit, Math.floor(Math.random() * 20) + 10);
  
  const templates = {
    threads: [
      "最新のゲーム情報をお届け！今週の注目タイトル",
      "話題のエンタメニュース速報",
      "注目のインディーゲーム紹介",
      "週末に遊びたいゲーム特集",
      "ゲーム実況配信の告知",
      "新作ゲームレビュー"
    ],
    twitter: [
      "ビジネストレンド最前線",
      "マーケティング成功事例を解説",
      "起業家インタビュー特集",
      "最新のビジネスツール紹介",
      "業界ニュース速報",
      "ビジネススキル向上のヒント"
    ],
    instagram: [
      "おしゃれカフェ巡りレポート",
      "週末グルメ探訪記",
      "ライフスタイル提案",
      "インテリアコーディネート術",
      "健康的な朝食レシピ",
      "季節のファッションコーデ"
    ]
  };
  
  for (let i = 0; i < postCount; i++) {
    const likes = Math.floor(Math.random() * 1000) + 50;
    const keyword = target.keywords[Math.floor(Math.random() * target.keywords.length)];
    const templateList = templates[target.platform] || templates.threads;
    const baseText = templateList[Math.floor(Math.random() * templateList.length)];
    
    mockPosts.push({
      postText: `${baseText} - ${keyword}関連の最新情報 #${i + 1}`,
      imageUrl: `https://picsum.photos/400/400?random=${Date.now()}-${i}`,
      likes: likes,
      genre: keyword,
      platform: target.platform,
      scraped_at: new Date().toISOString()
    });
  }
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
  
  return mockPosts;
};

// Generate CSV content from scraped data (with proper newlines)
const generateCSVContent = (data) => {
  const headers = ['投稿文', '画像URL', 'いいね数', 'ジャンル'];
  const rows = data.map(item => [
    `"${item.postText.replace(/"/g, '""')}"`,
    `"${item.imageUrl}"`,
    item.likes,
    `"${item.genre}"`
  ]);
  
  // Use actual newlines, not literal \n
  return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
};

// Start scraping scheduler
const startScrapingScheduler = () => {
  if (automationState.scrapingScheduler) {
    automationState.scrapingScheduler.destroy();
  }
  
  // Schedule scraping every X hours
  const interval = settings.SCRAPING_INTERVAL_HOURS || 8;
  const cronPattern = `0 */${interval} * * *`; // Every X hours
  
  automationState.scrapingScheduler = cron.schedule(cronPattern, async () => {
    if (automationState.isRunning && settings.SCRAPING_ENABLED) {
      console.log('🕷️ Starting scheduled scraping...');
      try {
        await runEasyScraper();
      } catch (error) {
        console.error('Scheduled scraping failed:', error);
      }
    }
  });
  
  // Schedule daily reset at midnight
  cron.schedule('0 0 * * *', resetDailyCounter);
  
  // Schedule periodic post scheduling check every 5 minutes
  if (automationState.postScheduler) {
    automationState.postScheduler.destroy();
  }
  automationState.postScheduler = cron.schedule('*/5 * * * *', async () => {
    if (automationState.isRunning) {
      await scheduleAutoPosts();
    }
  });
  
  // Set next scraping time
  const nextTime = new Date();
  nextTime.setHours(nextTime.getHours() + interval);
  automationState.nextScraping = nextTime.toISOString();
  
  console.log(`🕷️ Scraping scheduler started: every ${interval} hours`);
  console.log(`📮 Post scheduler started: every 5 minutes`);
};

// Update queue count
const updateQueueCount = async () => {
  return new Promise((resolve) => {
    db.get(`
      SELECT COUNT(*) as count 
      FROM posts 
      WHERE status = 'pending'
    `, (err, row) => {
      if (!err && row) {
        automationState.queuedPosts = row.count;
        console.log(`📊 Queue updated: ${automationState.queuedPosts} posts pending`);
      }
      resolve();
    });
  });
};

// ===================
// API ENDPOINTS
// ===================

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    message: 'Perfect Threads Auto Post System',
    version: 'v5.0-perfect',
    timestamp: new Date().toISOString(),
    automation_running: automationState.isRunning
  });
});

// Get all posts
app.get('/api/posts', (req, res) => {
  db.all(`
    SELECT * FROM posts 
    ORDER BY created_at DESC
    LIMIT 100
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
app.post('/api/posts', async (req, res) => {
  const posts = Array.isArray(req.body) ? req.body : [req.body];
  
  try {
    const savedCount = await savePostsToDatabase(posts);
    await updateQueueCount();
    
    res.json({
      success: true,
      saved_count: savedCount,
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
    
    const processedPosts = [];
    for (let i = 0; i < Math.min(csv_data.length, 10); i++) {
      const item = csv_data[i];
      const aiResult = await generateWithClaude(item.postText, csv_data);
      
      const scheduledDate = new Date();
      scheduledDate.setMinutes(scheduledDate.getMinutes() + (i + 1) * 60);
      
      processedPosts.push({
        id: `csv-${Date.now()}-${i}`,
        text: aiResult.improved_text,
        imageUrls: item.imageUrl ? [item.imageUrl] : [],
        genre: item.genre || 'general',
        scheduledTime: scheduledDate.toISOString(),
        status: 'pending',
        conceptSource: 'csv_upload',
        referencePost: item.postText,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
    }
    
    const savedCount = await savePostsToDatabase(processedPosts);
    await updateQueueCount();

    res.json({
      success: true,
      posts: processedPosts,
      processed_count: savedCount,
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
      bufferSchedule: true,
      SCRAPING_ENABLED: settings.SCRAPING_ENABLED,
      SCRAPING_INTERVAL_HOURS: settings.SCRAPING_INTERVAL_HOURS
    }
  });
});

app.post('/api/automation/settings', async (req, res) => {
  try {
    // Update settings
    Object.assign(settings, req.body);
    
    // Save to file
    await fs.writeFile('./settings.json', JSON.stringify(settings, null, 2));
    
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
app.get('/api/automation/status', async (req, res) => {
  await updateQueueCount();
  
  // Calculate next scheduled time
  let nextScheduled = automationState.nextScheduled;
  
  if (!nextScheduled && automationState.isRunning && automationState.queuedPosts > 0) {
    db.get(`
      SELECT MIN(scheduled_time) as next_time 
      FROM posts 
      WHERE status = 'pending'
      ORDER BY scheduled_time ASC
      LIMIT 1
    `, (err, row) => {
      if (!err && row && row.next_time) {
        nextScheduled = row.next_time;
      }
      
      res.json({
        success: true,
        status: {
          isRunning: automationState.isRunning,
          lastProcessed: automationState.lastProcessed,
          todayPosts: automationState.todayPosts,
          queuedPosts: automationState.queuedPosts,
          nextScheduled: nextScheduled,
          lastScraping: automationState.lastScraping,
          nextScraping: automationState.nextScraping
        }
      });
    });
  } else {
    res.json({
      success: true,
      status: {
        isRunning: automationState.isRunning,
        lastProcessed: automationState.lastProcessed,
        todayPosts: automationState.todayPosts,
        queuedPosts: automationState.queuedPosts,
        nextScheduled: nextScheduled,
        lastScraping: automationState.lastScraping,
        nextScraping: automationState.nextScraping
      }
    });
  }
});

// Start automation
app.post('/api/automation/start', async (req, res) => {
  try {
    console.log('\n🚀 Starting automation system...');
    automationState.isRunning = true;
    
    // Start CSV watcher
    await startCSVWatcher();
    
    // Start scraping scheduler
    startScrapingScheduler();
    
    // Update queue count
    await updateQueueCount();
    
    // Check for immediate posts
    await scheduleAutoPosts();
    
    logAutomationActivity('automation_started', 'success', 'Automation system started');
    
    res.json({
      success: true,
      message: '🤖 自動投稿システムを開始しました！CSV監視とスケジュール投稿が有効になります。'
    });
  } catch (error) {
    console.error('❌ Failed to start automation:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Stop automation
app.post('/api/automation/stop', (req, res) => {
  try {
    console.log('\n🛑 Stopping automation system...');
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
    
    // Stop post scheduler
    if (automationState.postScheduler) {
      automationState.postScheduler.destroy();
      automationState.postScheduler = null;
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
    WHERE action LIKE '%scraping%' OR action LIKE '%csv_processed%'
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

// Delete post
app.delete('/api/posts/:id', (req, res) => {
  const { id } = req.params;
  
  db.run('DELETE FROM posts WHERE id = ?', [id], async function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    await updateQueueCount();
    
    res.json({
      success: true,
      deleted: this.changes > 0
    });
  });
});

// Update post
app.put('/api/posts/:id', async (req, res) => {
  const { id } = req.params;
  const { text, imageUrls, genre, scheduledTime } = req.body;
  
  db.run(`
    UPDATE posts 
    SET text = ?, image_urls = ?, genre = ?, scheduled_time = ?, updated_at = ?
    WHERE id = ?
  `, [
    text,
    JSON.stringify(imageUrls),
    genre,
    scheduledTime,
    new Date().toISOString(),
    id
  ], async function(err) {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    await updateQueueCount();
    
    res.json({
      success: true,
      updated: this.changes > 0
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
  await fs.ensureDir('./csv_input/processed');
  
  // Initialize database (with clean start)
  initDatabase();
  
  // Wait a bit for database to initialize
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Start server
  app.listen(PORT, () => {
    console.log(`\n🚀 Perfect Threads Auto Post Server running on http://localhost:${PORT}`);
    console.log(`📊 CSV Watch Folder: ${settings.CSV_WATCH_FOLDER || './csv_input'}`);
    console.log(`🤖 AI Model: ${settings.AI_MODEL || 'claude-3-haiku-20240307'}`);
    console.log(`⚙️  Settings loaded from settings.json`);
    console.log(`\n✨ Ready to process CSV files!`);
    console.log(`💡 Start automation to begin processing existing CSV files`);
  });
};

startServer().catch(console.error);