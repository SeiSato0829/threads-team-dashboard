import express from 'express';
import multer from 'multer';
import { parse } from 'csv-parse/sync';
import { getDatabase } from '../database/index.js';
import claudeService from '../services/claude.js';
import logger from '../utils/logger.js';
import { authenticateUser } from '../middleware/auth.js';
import fs from 'fs-extra';

const router = express.Router();

// Configure multer for CSV uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/csv/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'csv-' + uniqueSuffix + '.csv');
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/csv' || file.originalname.endsWith('.csv')) {
      return cb(null, true);
    }
    cb(new Error('Only CSV files are allowed'));
  }
});

// Upload and process CSV
router.post('/upload', authenticateUser, upload.single('csv'), async (req, res) => {
  try {
    const { topCount = 10, removeDuplicates = true } = req.body;
    const db = getDatabase();
    
    // Read and parse CSV
    const csvContent = await fs.readFile(req.file.path, 'utf-8');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    // Create CSV import record
    const importResult = await db.run(`
      INSERT INTO csv_imports (user_id, filename, total_rows, status)
      VALUES (?, ?, ?, 'processing')
    `, [req.user.id, req.file.originalname, records.length]);
    
    const importId = importResult.lastID;
    
    // Process records
    let processedRecords = records.map(record => ({
      content: record.content || record.text || record.post_content || '',
      likes: parseInt(record.likes || record.like_count || record.reactions || 0),
      comments: parseInt(record.comments || record.comment_count || 0),
      shares: parseInt(record.shares || record.share_count || 0),
      author: record.author || record.username || '',
      url: record.url || record.post_url || '',
      posted_at: record.posted_at || record.date || new Date().toISOString()
    }));
    
    // Sort by likes and get top N
    processedRecords.sort((a, b) => b.likes - a.likes);
    processedRecords = processedRecords.slice(0, topCount);
    
    // Remove duplicates if requested
    if (removeDuplicates) {
      const seen = new Set();
      processedRecords = processedRecords.filter(record => {
        const normalized = record.content.toLowerCase().trim();
        if (seen.has(normalized)) {
          return false;
        }
        seen.add(normalized);
        return true;
      });
    }
    
    // Save popular posts to database
    for (const record of processedRecords) {
      await db.run(`
        INSERT INTO popular_posts (
          csv_import_id, original_content, likes_count, comments_count, 
          shares_count, author_username, post_url, posted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `, [
        importId,
        record.content,
        record.likes,
        record.comments,
        record.shares,
        record.author,
        record.url,
        record.posted_at
      ]);
    }
    
    // Update import status
    await db.run(`
      UPDATE csv_imports 
      SET status = 'completed', processed_rows = ?, updated_at = datetime('now')
      WHERE id = ?
    `, [processedRecords.length, importId]);
    
    // Get analysis from Claude
    const analysis = await claudeService.analyzePosts(processedRecords);
    
    res.json({
      message: 'CSV processed successfully',
      import: {
        id: importId,
        totalRows: records.length,
        processedRows: processedRecords.length
      },
      topPosts: processedRecords,
      analysis: analysis.analysis
    });
  } catch (error) {
    logger.error('CSV processing error:', error);
    res.status(500).json({ error: 'Failed to process CSV' });
  }
});

// Get CSV imports history
router.get('/imports', authenticateUser, async (req, res) => {
  try {
    const db = getDatabase();
    
    const imports = await db.all(`
      SELECT * FROM csv_imports 
      WHERE user_id = ? 
      ORDER BY created_at DESC
    `, [req.user.id]);
    
    res.json({ imports });
  } catch (error) {
    logger.error('Error fetching imports:', error);
    res.status(500).json({ error: 'Failed to fetch imports' });
  }
});

// Get popular posts from an import
router.get('/imports/:id/posts', authenticateUser, async (req, res) => {
  try {
    const db = getDatabase();
    
    // Verify import belongs to user
    const csvImport = await db.get(`
      SELECT * FROM csv_imports 
      WHERE id = ? AND user_id = ?
    `, [req.params.id, req.user.id]);
    
    if (!csvImport) {
      return res.status(404).json({ error: 'Import not found' });
    }
    
    const posts = await db.all(`
      SELECT * FROM popular_posts 
      WHERE csv_import_id = ? 
      ORDER BY likes_count DESC
    `, [req.params.id]);
    
    res.json({ 
      import: csvImport,
      posts 
    });
  } catch (error) {
    logger.error('Error fetching popular posts:', error);
    res.status(500).json({ error: 'Failed to fetch posts' });
  }
});

// Generate posts from CSV data
router.post('/generate-posts', authenticateUser, async (req, res) => {
  try {
    const { importId, theme, count = 5 } = req.body;
    const db = getDatabase();
    
    // Get top posts from import
    const topPosts = await db.all(`
      SELECT original_content as content, likes_count as likes 
      FROM popular_posts 
      WHERE csv_import_id = ? 
      ORDER BY likes_count DESC 
      LIMIT 5
    `, [importId]);
    
    if (topPosts.length === 0) {
      return res.status(400).json({ error: 'No posts found for this import' });
    }
    
    // Generate multiple posts
    const generatedPosts = [];
    
    for (let i = 0; i < count; i++) {
      const generated = await claudeService.generatePost(
        theme || 'ビジネス・起業',
        topPosts
      );
      
      // Save as draft
      const result = await db.run(`
        INSERT INTO posts (
          user_id, content, genre, status, ai_generated, 
          reference_posts, created_at
        )
        VALUES (?, ?, ?, 'draft', 1, ?, datetime('now'))
      `, [
        req.user.id,
        generated.content,
        theme || 'ビジネス・起業',
        JSON.stringify(topPosts.map(p => p.content))
      ]);
      
      const post = await db.get('SELECT * FROM posts WHERE id = ?', [result.lastID]);
      generatedPosts.push(post);
    }
    
    res.json({
      message: `Generated ${generatedPosts.length} posts successfully`,
      posts: generatedPosts
    });
  } catch (error) {
    logger.error('Error generating posts:', error);
    res.status(500).json({ error: 'Failed to generate posts' });
  }
});

export default router;