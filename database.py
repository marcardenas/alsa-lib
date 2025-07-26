import sqlite3
import hashlib
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for Trump monitoring"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create posts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id TEXT UNIQUE NOT NULL,
                        platform TEXT NOT NULL,
                        content TEXT NOT NULL,
                        post_hash TEXT UNIQUE NOT NULL,
                        created_at TEXT NOT NULL,
                        discovered_at TEXT NOT NULL,
                        url TEXT,
                        media_urls TEXT,
                        engagement_metrics TEXT,
                        sent_notification BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Create notifications table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        sent_at TEXT NOT NULL,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        FOREIGN KEY (post_id) REFERENCES posts (post_id)
                    )
                ''')
                
                # Create monitoring_log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS monitoring_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        platform TEXT NOT NULL,
                        check_time TEXT NOT NULL,
                        posts_found INTEGER DEFAULT 0,
                        new_posts INTEGER DEFAULT 0,
                        status TEXT NOT NULL,
                        error_message TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def generate_post_hash(self, content: str, platform: str) -> str:
        """Generate a unique hash for a post based on content and platform"""
        hash_input = f"{platform}:{content}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()
    
    def is_post_new(self, post_hash: str) -> bool:
        """Check if a post is new (not in database)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM posts WHERE post_hash = ?', (post_hash,))
                return cursor.fetchone() is None
        except sqlite3.Error as e:
            logger.error(f"Error checking post existence: {e}")
            return False
    
    def save_post(self, post_data: Dict[str, Any]) -> bool:
        """Save a new post to the database"""
        try:
            post_hash = self.generate_post_hash(post_data['content'], post_data['platform'])
            
            # Check if post already exists
            if not self.is_post_new(post_hash):
                logger.debug(f"Post already exists: {post_data.get('post_id', 'unknown')}")
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO posts (
                        post_id, platform, content, post_hash, created_at, 
                        discovered_at, url, media_urls, engagement_metrics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post_data.get('post_id'),
                    post_data.get('platform'),
                    post_data.get('content'),
                    post_hash,
                    post_data.get('created_at'),
                    datetime.now().isoformat(),
                    post_data.get('url'),
                    post_data.get('media_urls'),
                    post_data.get('engagement_metrics')
                ))
                conn.commit()
                logger.info(f"New post saved: {post_data.get('post_id')} from {post_data.get('platform')}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error saving post: {e}")
            return False
    
    def mark_notification_sent(self, post_id: str, platform: str, status: str = "sent", error_message: str = None) -> bool:
        """Mark a post as having notification sent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update posts table
                cursor.execute('''
                    UPDATE posts SET sent_notification = TRUE 
                    WHERE post_id = ? AND platform = ?
                ''', (post_id, platform))
                
                # Insert notification record
                cursor.execute('''
                    INSERT INTO notifications (post_id, platform, sent_at, status, error_message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (post_id, platform, datetime.now().isoformat(), status, error_message))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error marking notification sent: {e}")
            return False
    
    def get_unsent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get posts that haven't had notifications sent yet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT post_id, platform, content, created_at, url, media_urls, engagement_metrics
                    FROM posts 
                    WHERE sent_notification = FALSE 
                    ORDER BY discovered_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting unsent posts: {e}")
            return []
    
    def log_monitoring_check(self, platform: str, posts_found: int, new_posts: int, status: str, error_message: str = None):
        """Log a monitoring check"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO monitoring_log (platform, check_time, posts_found, new_posts, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (platform, datetime.now().isoformat(), posts_found, new_posts, status, error_message))
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Error logging monitoring check: {e}")
    
    def get_recent_posts(self, platform: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent posts, optionally filtered by platform"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if platform:
                    cursor.execute('''
                        SELECT * FROM posts 
                        WHERE platform = ? 
                        ORDER BY discovered_at DESC 
                        LIMIT ?
                    ''', (platform, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM posts 
                        ORDER BY discovered_at DESC 
                        LIMIT ?
                    ''', (limit,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting recent posts: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total posts by platform
                cursor.execute('''
                    SELECT platform, COUNT(*) as count 
                    FROM posts 
                    GROUP BY platform
                ''')
                platform_stats = dict(cursor.fetchall())
                
                # Total notifications sent
                cursor.execute('SELECT COUNT(*) FROM notifications WHERE status = "sent"')
                notifications_sent = cursor.fetchone()[0]
                
                # Recent monitoring activity
                cursor.execute('''
                    SELECT platform, COUNT(*) as checks, 
                           SUM(new_posts) as total_new_posts,
                           MAX(check_time) as last_check
                    FROM monitoring_log 
                    WHERE check_time > datetime('now', '-24 hours')
                    GROUP BY platform
                ''')
                
                columns = [description[0] for description in cursor.description]
                recent_activity = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return {
                    'platform_stats': platform_stats,
                    'notifications_sent': notifications_sent,
                    'recent_activity': recent_activity
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            return {}