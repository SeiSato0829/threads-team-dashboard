import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs-extra';
import logger from '../utils/logger.js';

const BUFFER_API_URL = 'https://api.bufferapp.com/1';

class BufferService {
  constructor() {
    this.accessToken = process.env.BUFFER_ACCESS_TOKEN;
    this.profileId = process.env.BUFFER_PROFILE_ID;
    
    if (!this.accessToken || !this.profileId) {
      logger.warn('Buffer API credentials not configured');
    }
  }

  async createPost(content, mediaUrls = [], scheduledAt = null) {
    try {
      const postData = {
        text: content,
        profile_ids: [this.profileId],
        shorten: true,
        now: !scheduledAt
      };

      if (scheduledAt) {
        postData.scheduled_at = Math.floor(new Date(scheduledAt).getTime() / 1000);
      }

      // Handle media uploads
      if (mediaUrls.length > 0) {
        const mediaIds = await this.uploadMedia(mediaUrls);
        postData.media = { picture: mediaIds };
      }

      const response = await axios.post(
        `${BUFFER_API_URL}/updates/create.json`,
        postData,
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      logger.info('Buffer post created successfully:', response.data);
      return response.data;
    } catch (error) {
      logger.error('Buffer API error:', error.response?.data || error.message);
      throw new Error(`Failed to create Buffer post: ${error.message}`);
    }
  }

  async uploadMedia(mediaUrls) {
    const mediaIds = [];

    for (const mediaUrl of mediaUrls) {
      try {
        const formData = new FormData();
        
        // If it's a local file path
        if (mediaUrl.startsWith('/') || mediaUrl.startsWith('uploads/')) {
          const stream = fs.createReadStream(mediaUrl);
          formData.append('photo', stream);
        } else {
          // If it's a URL, download first
          const response = await axios.get(mediaUrl, { responseType: 'stream' });
          formData.append('photo', response.data);
        }

        const uploadResponse = await axios.post(
          `${BUFFER_API_URL}/updates/photos/upload.json`,
          formData,
          {
            headers: {
              ...formData.getHeaders(),
              'Authorization': `Bearer ${this.accessToken}`
            }
          }
        );

        if (uploadResponse.data.media_id) {
          mediaIds.push(uploadResponse.data.media_id);
        }
      } catch (error) {
        logger.error('Media upload error:', error.message);
      }
    }

    return mediaIds;
  }

  async updatePost(updateId, content, scheduledAt = null) {
    try {
      const updateData = {
        text: content,
        update_id: updateId
      };

      if (scheduledAt) {
        updateData.scheduled_at = Math.floor(new Date(scheduledAt).getTime() / 1000);
      }

      const response = await axios.post(
        `${BUFFER_API_URL}/updates/${updateId}/update.json`,
        updateData,
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      logger.info('Buffer post updated successfully:', response.data);
      return response.data;
    } catch (error) {
      logger.error('Buffer update error:', error.response?.data || error.message);
      throw new Error(`Failed to update Buffer post: ${error.message}`);
    }
  }

  async deletePost(updateId) {
    try {
      const response = await axios.post(
        `${BUFFER_API_URL}/updates/${updateId}/destroy.json`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        }
      );

      logger.info('Buffer post deleted successfully');
      return response.data;
    } catch (error) {
      logger.error('Buffer delete error:', error.response?.data || error.message);
      throw new Error(`Failed to delete Buffer post: ${error.message}`);
    }
  }

  async getProfile() {
    try {
      const response = await axios.get(
        `${BUFFER_API_URL}/profiles/${this.profileId}.json`,
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        }
      );

      return response.data;
    } catch (error) {
      logger.error('Buffer profile error:', error.response?.data || error.message);
      throw new Error(`Failed to get Buffer profile: ${error.message}`);
    }
  }

  async getScheduledPosts() {
    try {
      const response = await axios.get(
        `${BUFFER_API_URL}/profiles/${this.profileId}/updates/pending.json`,
        {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        }
      );

      return response.data.updates || [];
    } catch (error) {
      logger.error('Buffer scheduled posts error:', error.response?.data || error.message);
      throw new Error(`Failed to get scheduled posts: ${error.message}`);
    }
  }
}

export default new BufferService();