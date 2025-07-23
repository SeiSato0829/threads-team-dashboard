import cron from 'node-cron';
import { getDatabase } from '../database/index.js';
import bufferService from './buffer.js';
import logger from '../utils/logger.js';

class SchedulerService {
  constructor() {
    this.scheduledJobs = new Map();
  }

  async initializeScheduler() {
    logger.info('Initializing scheduler...');
    
    // Run every 15 minutes to check for posts to schedule
    cron.schedule('*/15 * * * *', async () => {
      await this.checkAndSchedulePosts();
    });

    // Run daily at 2 AM to clean up old data
    cron.schedule('0 2 * * *', async () => {
      await this.cleanupOldData();
    });

    // Initial check on startup
    await this.checkAndSchedulePosts();
    
    logger.info('Scheduler initialized successfully');
  }

  async checkAndSchedulePosts() {
    try {
      const db = getDatabase();
      const now = new Date();
      const fifteenMinutesFromNow = new Date(now.getTime() + 15 * 60 * 1000);

      // Find posts that need to be scheduled to Buffer
      const postsToSchedule = await db.all(`
        SELECT * FROM posts 
        WHERE status = 'scheduled' 
        AND scheduled_for <= datetime(?)
        AND scheduled_for > datetime(?)
        AND buffer_post_id IS NULL
        ORDER BY scheduled_for ASC
      `, [
        fifteenMinutesFromNow.toISOString(),
        now.toISOString()
      ]);

      logger.info(`Found ${postsToSchedule.length} posts to schedule`);

      for (const post of postsToSchedule) {
        await this.schedulePost(post);
      }
    } catch (error) {
      logger.error('Error checking posts to schedule:', error);
    }
  }

  async schedulePost(post) {
    try {
      logger.info(`Scheduling post ${post.id} for ${post.scheduled_for}`);

      // Parse media URLs if any
      const mediaUrls = post.media_urls ? JSON.parse(post.media_urls) : [];

      // Create post in Buffer
      const bufferResponse = await bufferService.createPost(
        post.content,
        mediaUrls,
        post.scheduled_for
      );

      // Update post with Buffer ID
      const db = getDatabase();
      await db.run(`
        UPDATE posts 
        SET buffer_post_id = ?, 
            status = 'buffer_scheduled',
            updated_at = datetime('now')
        WHERE id = ?
      `, [bufferResponse.id, post.id]);

      logger.info(`Post ${post.id} scheduled successfully with Buffer ID ${bufferResponse.id}`);

      // Log API call
      await this.logApiCall(post.user_id, 'buffer', 'create_post', {
        postId: post.id,
        bufferId: bufferResponse.id
      });
    } catch (error) {
      logger.error(`Error scheduling post ${post.id}:`, error);
      
      // Update post status to error
      const db = getDatabase();
      await db.run(`
        UPDATE posts 
        SET status = 'error',
            updated_at = datetime('now')
        WHERE id = ?
      `, [post.id]);

      // Log failed API call
      await this.logApiCall(post.user_id, 'buffer', 'create_post_error', {
        postId: post.id,
        error: error.message
      });
    }
  }

  async cleanupOldData() {
    try {
      const db = getDatabase();
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

      // Delete old API logs
      await db.run(`
        DELETE FROM api_logs 
        WHERE created_at < datetime(?)
      `, [thirtyDaysAgo.toISOString()]);

      // Delete old completed posts
      await db.run(`
        DELETE FROM posts 
        WHERE status = 'published' 
        AND created_at < datetime(?)
      `, [thirtyDaysAgo.toISOString()]);

      logger.info('Cleanup completed successfully');
    } catch (error) {
      logger.error('Error during cleanup:', error);
    }
  }

  async logApiCall(userId, apiName, endpoint, data) {
    try {
      const db = getDatabase();
      await db.run(`
        INSERT INTO api_logs (user_id, api_name, endpoint, request_data, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
      `, [
        userId,
        apiName,
        endpoint,
        JSON.stringify(data)
      ]);
    } catch (error) {
      logger.error('Error logging API call:', error);
    }
  }

  async updatePostStatus(postId, status) {
    try {
      const db = getDatabase();
      await db.run(`
        UPDATE posts 
        SET status = ?,
            updated_at = datetime('now')
        WHERE id = ?
      `, [status, postId]);
      
      logger.info(`Updated post ${postId} status to ${status}`);
    } catch (error) {
      logger.error(`Error updating post ${postId} status:`, error);
    }
  }

  // Check Buffer for post status updates
  async syncBufferStatus() {
    try {
      const db = getDatabase();
      
      // Get all posts scheduled in Buffer
      const bufferScheduledPosts = await db.all(`
        SELECT * FROM posts 
        WHERE status = 'buffer_scheduled' 
        AND buffer_post_id IS NOT NULL
      `);

      const scheduledBufferPosts = await bufferService.getScheduledPosts();
      const scheduledIds = new Set(scheduledBufferPosts.map(p => p.id));

      for (const post of bufferScheduledPosts) {
        if (!scheduledIds.has(post.buffer_post_id)) {
          // Post no longer in Buffer's queue, likely published
          await this.updatePostStatus(post.id, 'published');
        }
      }
    } catch (error) {
      logger.error('Error syncing Buffer status:', error);
    }
  }
}

export default new SchedulerService();
export const initializeScheduler = () => new SchedulerService().initializeScheduler();