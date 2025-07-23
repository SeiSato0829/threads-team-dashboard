import express from 'express';
import claudeService from '../services/claude.js';
import logger from '../utils/logger.js';
import { authenticateUser } from '../middleware/auth.js';

const router = express.Router();

// Generate post content
router.post('/generate', authenticateUser, async (req, res) => {
  try {
    const { theme, referencePosts = [], maxLength = 500 } = req.body;
    
    const generated = await claudeService.generatePost(theme, referencePosts, maxLength);
    
    res.json({
      message: 'Content generated successfully',
      generated
    });
  } catch (error) {
    logger.error('AI generation error:', error);
    res.status(500).json({ error: 'Failed to generate content' });
  }
});

// Improve existing content
router.post('/improve', authenticateUser, async (req, res) => {
  try {
    const { content, theme, maxLength = 500 } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }
    
    const improved = await claudeService.improvePost(content, theme, maxLength);
    
    res.json({
      message: 'Content improved successfully',
      improved
    });
  } catch (error) {
    logger.error('AI improvement error:', error);
    res.status(500).json({ error: 'Failed to improve content' });
  }
});

// Generate hashtags
router.post('/hashtags', authenticateUser, async (req, res) => {
  try {
    const { content, maxHashtags = 3 } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required' });
    }
    
    const hashtags = await claudeService.generateHashtags(content, maxHashtags);
    
    res.json({
      message: 'Hashtags generated successfully',
      hashtags
    });
  } catch (error) {
    logger.error('AI hashtag error:', error);
    res.status(500).json({ error: 'Failed to generate hashtags' });
  }
});

// Test AI connection
router.get('/test', authenticateUser, async (req, res) => {
  try {
    const testGenerated = await claudeService.generatePost('テスト投稿', [], 100);
    res.json({ 
      status: 'connected',
      test: testGenerated.content.substring(0, 50) + '...'
    });
  } catch (error) {
    logger.error('AI test error:', error);
    res.status(500).json({ 
      status: 'error',
      error: 'Failed to connect to Claude API' 
    });
  }
});

export default router;