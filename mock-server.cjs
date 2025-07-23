const express = require('express');
const cors = require('cors');
const multer = require('multer');

const app = express();
const PORT = 5000;

// Configure multer for file uploads
const upload = multer({ dest: 'uploads/' });

// Enable CORS for all routes
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    message: 'Mock server is running',
    version: 'v3.2-mock',
    timestamp: new Date().toISOString()
  });
});

// Mock posts storage
let mockPosts = [];

// Get posts endpoint
app.get('/api/posts', (req, res) => {
  res.json({
    posts: mockPosts,
    total: mockPosts.length
  });
});

// Save posts endpoint
app.post('/api/posts', (req, res) => {
  console.log('Received posts:', req.body);
  const newPosts = Array.isArray(req.body) ? req.body : [req.body];
  mockPosts.push(...newPosts);
  res.json({
    success: true,
    saved_count: newPosts.length,
    message: 'Posts saved successfully (mock)'
  });
});

// CSV processing endpoint
app.post('/api/csv/process', (req, res) => {
  console.log('CSV processing request:', req.body);
  const { csv_data, company_concepts } = req.body;
  
  // Mock CSV processing
  const processedPosts = csv_data.slice(0, 10).map((item, index) => ({
    id: `csv-${Date.now()}-${index}`,
    text: `AI改良版: ${item.postText}`,
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
    message: 'CSV processed successfully (mock)'
  });
});

// AI post generation endpoint
app.post('/api/ai/generate', (req, res) => {
  console.log('AI generation request:', req.body);
  const { text, genre, reference_posts } = req.body;
  
  // Mock AI improvement
  const improvedText = `AI改良版: ${text}
#${genre} #人気投稿をもとにAIが改良しました`;

  res.json({
    success: true,
    improved_text: improvedText,
    confidence: 0.85,
    message: 'Post improved by AI (mock)'
  });
});

// Image upload endpoint
app.post('/api/upload/image', upload.single('image'), (req, res) => {
  console.log('Image upload request:', req.file);
  
  if (!req.file) {
    return res.status(400).json({
      success: false,
      message: 'No image file provided'
    });
  }

  // Mock image URL
  const mockImageUrl = `http://localhost:5000/images/${req.file.filename}`;
  
  res.json({
    success: true,
    url: mockImageUrl,
    filename: req.file.filename,
    message: 'Image uploaded successfully (mock)'
  });
});

// Schedule post endpoint
app.post('/api/schedule', (req, res) => {
  console.log('Schedule post request:', req.body);
  const { text, scheduled_time, image_urls } = req.body;
  
  res.json({
    success: true,
    buffer_send_time: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    schedule_id: `schedule-${Date.now()}`,
    message: 'Post scheduled successfully (mock)'
  });
});

// Settings endpoints
app.get('/api/settings', (req, res) => {
  res.json({
    settings: {
      claude_api_key: '****',
      buffer_access_token: '****'
    },
    message: 'Settings retrieved (mock)'
  });
});

app.post('/api/settings', (req, res) => {
  console.log('Settings update:', req.body);
  res.json({
    success: true,
    message: 'Settings updated successfully (mock)'
  });
});

// Automation endpoints
let automationRunning = false;
let automationSettings = {
  enabled: false,
  csvWatchFolder: './csv_input',
  postInterval: 60,
  dailyPostLimit: 10,
  postTimeStart: '09:00',
  postTimeEnd: '21:00',
  autoGenerate: true,
  bufferSchedule: true
};

app.get('/api/automation/settings', (req, res) => {
  res.json({
    success: true,
    settings: automationSettings
  });
});

app.post('/api/automation/settings', (req, res) => {
  console.log('Automation settings update:', req.body);
  automationSettings = { ...automationSettings, ...req.body };
  res.json({
    success: true,
    message: 'Automation settings saved successfully'
  });
});

app.get('/api/automation/status', (req, res) => {
  const now = new Date();
  const nextScheduled = new Date(now.getTime() + automationSettings.postInterval * 60 * 1000);
  
  res.json({
    success: true,
    status: {
      isRunning: automationRunning,
      lastProcessed: automationRunning ? new Date(now.getTime() - 30 * 60 * 1000).toISOString() : null,
      todayPosts: Math.floor(Math.random() * 5), // Mock data
      queuedPosts: Math.floor(Math.random() * 10), // Mock data
      nextScheduled: automationRunning ? nextScheduled.toISOString() : null
    }
  });
});

app.post('/api/automation/start', (req, res) => {
  console.log('Starting automation...');
  automationRunning = true;
  res.json({
    success: true,
    message: '🤖 自動投稿システムを開始しました！CSV監視とスケジュール投稿が有効になります。'
  });
});

app.post('/api/automation/stop', (req, res) => {
  console.log('Stopping automation...');
  automationRunning = false;
  res.json({
    success: true,
    message: '🛑 自動投稿システムを停止しました。'
  });
});

app.listen(PORT, () => {
  console.log(`Mock server running on http://localhost:${PORT}`);
  console.log('Health check: http://localhost:5000/api/health');
});