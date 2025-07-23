import express from 'express';
import bufferService from '../services/buffer.js';
import logger from '../utils/logger.js';
import { authenticateUser } from '../middleware/auth.js';

const router = express.Router();

// Get Buffer profile info
router.get('/profile', authenticateUser, async (req, res) => {
  try {
    const profile = await bufferService.getProfile();
    res.json({ profile });
  } catch (error) {
    logger.error('Buffer profile error:', error);
    res.status(500).json({ error: 'Failed to fetch Buffer profile' });
  }
});

// Get scheduled posts from Buffer
router.get('/scheduled', authenticateUser, async (req, res) => {
  try {
    const posts = await bufferService.getScheduledPosts();
    res.json({ posts });
  } catch (error) {
    logger.error('Buffer scheduled posts error:', error);
    res.status(500).json({ error: 'Failed to fetch scheduled posts' });
  }
});

// Test Buffer connection
router.get('/test', authenticateUser, async (req, res) => {
  try {
    const profile = await bufferService.getProfile();
    res.json({ 
      status: 'connected',
      profile: {
        id: profile.id,
        service: profile.service,
        username: profile.service_username
      }
    });
  } catch (error) {
    logger.error('Buffer test error:', error);
    res.status(500).json({ 
      status: 'error',
      error: 'Failed to connect to Buffer' 
    });
  }
});

export default router;