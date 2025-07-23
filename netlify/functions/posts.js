import { Handler } from '@netlify/functions';
import { getDatabase } from '../../server/database/index.js';
import bufferService from '../../server/services/buffer.js';
import claudeService from '../../server/services/claude.js';

const handler = async (event, context) => {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  };

  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  try {
    const { httpMethod, path, body } = event;
    const parsedBody = body ? JSON.parse(body) : {};
    
    // Initialize database
    await initializeDatabase();
    const db = getDatabase();

    switch (httpMethod) {
      case 'GET':
        if (path.includes('/stats')) {
          const stats = await db.get(`
            SELECT 
              COUNT(*) as total,
              SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as drafts,
              SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
              SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published
            FROM posts
          `);
          
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ stats }),
          };
        } else {
          // Get all posts
          const posts = await db.all('SELECT * FROM posts ORDER BY created_at DESC');
          return {
            statusCode: 200,
            headers,
            body: JSON.stringify({ posts }),
          };
        }

      case 'POST':
        const { content, genre, scheduledFor, useAI } = parsedBody;
        
        let finalContent = content;
        if (useAI) {
          const improved = await claudeService.improvePost(content, genre);
          finalContent = improved.improved;
        }

        const result = await db.run(`
          INSERT INTO posts (content, genre, scheduled_for, status, ai_generated)
          VALUES (?, ?, ?, ?, ?)
        `, [
          finalContent,
          genre,
          scheduledFor,
          scheduledFor ? 'scheduled' : 'draft',
          useAI
        ]);

        const post = await db.get('SELECT * FROM posts WHERE id = ?', [result.lastID]);

        return {
          statusCode: 201,
          headers,
          body: JSON.stringify({ message: 'Post created', post }),
        };

      default:
        return {
          statusCode: 405,
          headers,
          body: JSON.stringify({ error: 'Method not allowed' }),
        };
    }
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Internal server error' }),
    };
  }
};

export { handler };