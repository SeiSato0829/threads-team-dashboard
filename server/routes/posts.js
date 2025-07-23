import express from 'express';
import { getDatabase } from '../database/index.js';
import bufferService from '../services/buffer.js';
import claudeService from '../services/claude.js';
import logger from '../utils/logger.js';
import { authenticateUser } from '../middleware/auth.js';
import multer from 'multer';
import path from 'path';

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image files are allowed'));
    }
  }
});

// Get all posts with filtering
router.get('/', authenticateUser, async (req, res) => {
  try {
    const db = getDatabase();
    const { status, genre, search, sort = 'created_at', order = 'DESC' } = req.query;
    
    let query = 'SELECT * FROM posts WHERE user_id = ?';
    const params = [req.user.id];
    
    if (status) {
      query += ' AND status = ?';
      params.push(status);
    }
    
    if (genre) {
      query += ' AND genre LIKE ?';
      params.push(`%${genre}%`);
    }
    
    if (search) {
      query += ' AND content LIKE ?';
      params.push(`%${search}%`);
    }
    
    query += ` ORDER BY ${sort} ${order}`;
    
    const posts = await db.all(query, params);
    
    res.json({ posts });
  } catch (error) {
    logger.error('Error fetching posts:', error);
    res.status(500).json({ error: 'Failed to fetch posts' });
  }
});

// Get post statistics
router.get('/stats', authenticateUser, async (req, res) => {
  try {
    const db = getDatabase();
    
    const stats = await db.get(`
      SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as drafts,
        SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
        SUM(CASE WHEN status = 'buffer_scheduled' THEN 1 ELSE 0 END) as buffer_scheduled,
        SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published,
        SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
        SUM(CASE WHEN ai_generated = 1 THEN 1 ELSE 0 END) as ai_generated
      FROM posts 
      WHERE user_id = ?
    `, [req.user.id]);
    
    res.json({ stats });
  } catch (error) {
    logger.error('Error fetching stats:', error);
    res.status(500).json({ error: 'Failed to fetch statistics' });
  }
});

// Create a new post
router.post('/', authenticateUser, upload.array('media', 4), async (req, res) => {
  try {
    const db = getDatabase();
    const { content, genre, scheduledFor, useAI } = req.body;
    
    let finalContent = content;
    let aiGenerated = false;
    
    // Use AI to improve content if requested
    if (useAI === 'true') {
      const improved = await claudeService.improvePost(content, genre);
      finalContent = improved.improved;
      aiGenerated = true;
    }
    
    // Handle media uploads
    const mediaUrls = req.files ? req.files.map(file => `/uploads/${file.filename}`) : [];
    
    // Insert post into database
    const result = await db.run(`
      INSERT INTO posts (user_id, content, media_urls, genre, scheduled_for, status, ai_generated)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `, [
      req.user.id,
      finalContent,
      JSON.stringify(mediaUrls),
      genre,
      scheduledFor,
      scheduledFor ? 'scheduled' : 'draft',
      aiGenerated
    ]);
    
    const post = await db.get('SELECT * FROM posts WHERE id = ?', [result.lastID]);
    
    res.json({ 
      message: 'Post created successfully',
      post 
    });
  } catch (error) {
    logger.error('Error creating post:', error);
    res.status(500).json({ error: 'Failed to create post' });
  }
});

// Update a post
router.put('/:id', authenticateUser, async (req, res) => {
  try {
    const db = getDatabase();
    const { content, genre, scheduledFor, status } = req.body;
    
    // Check if post belongs to user
    const post = await db.get('SELECT * FROM posts WHERE id = ? AND user_id = ?', [
      req.params.id,
      req.user.id
    ]);
    
    if (!post) {
      return res.status(404).json({ error: 'Post not found' });
    }
    
    // Update post
    await db.run(`
      UPDATE posts 
      SET content = ?, genre = ?, scheduled_for = ?, status = ?, updated_at = datetime('now')
      WHERE id = ? AND user_id = ?
    `, [
      content || post.content,
      genre || post.genre,
      scheduledFor || post.scheduled_for,
      status || post.status,
      req.params.id,
      req.user.id
    ]);
    
    // If post was already scheduled to Buffer, update it there too
    if (post.buffer_post_id && (content || scheduledFor)) {
      await bufferService.updatePost(post.buffer_post_id, content || post.content, scheduledFor);
    }
    
    const updatedPost = await db.get('SELECT * FROM posts WHERE id = ?', [req.params.id]);
    
    res.json({ 
      message: 'Post updated successfully',
      post: updatedPost 
    });
  } catch (error) {
    logger.error('Error updating post:', error);
    res.status(500).json({ error: 'Failed to update post' });
  }
});

// Delete a post
router.delete('/:id', authenticateUser, async (req, res) => {
  try {
    const db = getDatabase();
    
    // Check if post belongs to user
    const post = await db.get('SELECT * FROM posts WHERE id = ? AND user_id = ?', [
      req.params.id,
      req.user.id
    ]);
    
    if (!post) {
      return res.status(404).json({ error: 'Post not found' });
    }
    
    // If post was scheduled to Buffer, delete it there too
    if (post.buffer_post_id) {
      await bufferService.deletePost(post.buffer_post_id);
    }
    
    // Delete post from database
    await db.run('DELETE FROM posts WHERE id = ? AND user_id = ?', [
      req.params.id,
      req.user.id
    ]);
    
    res.json({ message: 'Post deleted successfully' });
  } catch (error) {
    logger.error('Error deleting post:', error);
    res.status(500).json({ error: 'Failed to delete post' });
  }
});

// Generate AI post from popular posts
router.post('/generate', authenticateUser, async (req, res) => {
  try {
    const { theme, referencePostIds = [] } = req.body;
    const db = getDatabase();
    
    let referencePosts = [];
    
    // Get reference posts if provided
    if (referencePostIds.length > 0) {
      referencePosts = await db.all(`
        SELECT original_content as content, likes_count as likes 
        FROM popular_posts 
        WHERE id IN (${referencePostIds.map(() => '?').join(',')})
        ORDER BY likes_count DESC
      `, referencePostIds);
    }
    
    // Generate post using Claude
    const generated = await claudeService.generatePost(theme, referencePosts);
    
    res.json({ 
      message: 'Post generated successfully',
      generated 
    });
  } catch (error) {
    logger.error('Error generating post:', error);
    res.status(500).json({ error: 'Failed to generate post' });
  }
});

export default router;