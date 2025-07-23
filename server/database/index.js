import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import logger from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let db;

export async function initializeDatabase() {
  try {
    // Open database connection
    db = await open({
      filename: join(__dirname, '../../threads_posts.db'),
      driver: sqlite3.Database
    });

    // Create tables
    await createTables();
    
    logger.info('Database initialized successfully');
    return db;
  } catch (error) {
    logger.error('Database initialization failed:', error);
    throw error;
  }
}

async function createTables() {
  // Users table
  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      name TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Posts table
  await db.exec(`
    CREATE TABLE IF NOT EXISTS posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      content TEXT NOT NULL,
      media_urls TEXT,
      genre TEXT,
      scheduled_for DATETIME,
      buffer_post_id TEXT,
      status TEXT DEFAULT 'draft',
      ai_generated BOOLEAN DEFAULT 0,
      reference_posts TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // CSV imports table
  await db.exec(`
    CREATE TABLE IF NOT EXISTS csv_imports (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      filename TEXT NOT NULL,
      total_rows INTEGER,
      processed_rows INTEGER,
      status TEXT DEFAULT 'pending',
      error_message TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // Popular posts table (for reference)
  await db.exec(`
    CREATE TABLE IF NOT EXISTS popular_posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      csv_import_id INTEGER,
      original_content TEXT,
      likes_count INTEGER,
      comments_count INTEGER,
      shares_count INTEGER,
      posted_at DATETIME,
      author_username TEXT,
      post_url TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (csv_import_id) REFERENCES csv_imports(id)
    )
  `);

  // API logs table
  await db.exec(`
    CREATE TABLE IF NOT EXISTS api_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      api_name TEXT NOT NULL,
      endpoint TEXT,
      request_data TEXT,
      response_data TEXT,
      status_code INTEGER,
      error_message TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // Create indexes
  await db.exec(`
    CREATE INDEX IF NOT EXISTS idx_posts_scheduled_for ON posts(scheduled_for);
    CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
    CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
    CREATE INDEX IF NOT EXISTS idx_csv_imports_user_id ON csv_imports(user_id);
    CREATE INDEX IF NOT EXISTS idx_popular_posts_likes ON popular_posts(likes_count DESC);
  `);
}

export function getDatabase() {
  if (!db) {
    throw new Error('Database not initialized. Call initializeDatabase() first.');
  }
  return db;
}

export default { initializeDatabase, getDatabase };