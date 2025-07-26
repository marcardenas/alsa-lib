import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import Config
from database import DatabaseManager
from whatsapp_client import WhatsAppClient
from social_media_monitors import SocialMediaAggregator

# Set up logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TrumpMonitorService:
    """Main service for monitoring Trump's social media activity"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.whatsapp = WhatsAppClient()
        self.social_aggregator = SocialMediaAggregator()
        self.scheduler = AsyncIOScheduler()
        
        self.is_running = False
        self.last_check_time = None
        
        logger.info("Trump Monitor Service initialized")
    
    async def start_monitoring(self):
        """Start the monitoring service"""
        try:
            # Validate configuration
            if not Config.validate_config():
                logger.error("Configuration validation failed")
                return False
            
            # Test WhatsApp connection
            logger.info("Testing WhatsApp connection...")
            if not self.whatsapp.test_connection():
                logger.error("WhatsApp connection test failed")
                return False
            
            # Send startup notification
            await self.send_startup_notification()
            
            # Schedule monitoring checks
            self.scheduler.add_job(
                self.check_for_new_posts,
                IntervalTrigger(minutes=Config.CHECK_INTERVAL_MINUTES),
                id='post_check',
                max_instances=1
            )
            
            # Schedule daily summary
            self.scheduler.add_job(
                self.send_daily_summary,
                IntervalTrigger(hours=24),
                id='daily_summary',
                max_instances=1
            )
            
            # Schedule notification processing
            self.scheduler.add_job(
                self.process_pending_notifications,
                IntervalTrigger(minutes=1),
                id='notification_processor',
                max_instances=1
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info("Trump Monitor Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring service: {e}")
            return False
    
    async def stop_monitoring(self):
        """Stop the monitoring service"""
        try:
            self.is_running = False
            self.scheduler.shutdown(wait=True)
            
            # Send shutdown notification
            await self.send_shutdown_notification()
            
            logger.info("Trump Monitor Service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring service: {e}")
    
    async def check_for_new_posts(self):
        """Check all platforms for new posts"""
        logger.info("Starting post check cycle")
        
        try:
            # Fetch posts from all platforms
            all_posts = self.social_aggregator.fetch_all_posts(
                limit_per_platform=Config.MAX_POSTS_PER_CHECK
            )
            
            new_posts_count = 0
            
            for post_data in all_posts:
                if self.db.save_post(post_data):
                    new_posts_count += 1
                    logger.info(f"New post detected from {post_data['platform']}: {post_data['post_id']}")
            
            # Log monitoring check
            for monitor in self.social_aggregator.monitors:
                platform_posts = [p for p in all_posts if p['platform'] == monitor.platform_name]
                platform_new_posts = sum(1 for p in platform_posts if self.db.is_post_new(
                    self.db.generate_post_hash(p['content'], p['platform'])
                ))
                
                self.db.log_monitoring_check(
                    platform=monitor.platform_name,
                    posts_found=len(platform_posts),
                    new_posts=platform_new_posts,
                    status="success"
                )
            
            self.last_check_time = datetime.now()
            logger.info(f"Post check completed. Found {new_posts_count} new posts")
            
        except Exception as e:
            logger.error(f"Error during post check: {e}")
            
            # Log error for all platforms
            for monitor in self.social_aggregator.monitors:
                self.db.log_monitoring_check(
                    platform=monitor.platform_name,
                    posts_found=0,
                    new_posts=0,
                    status="error",
                    error_message=str(e)
                )
    
    async def process_pending_notifications(self):
        """Process posts that need notifications sent"""
        try:
            unsent_posts = self.db.get_unsent_posts(limit=10)
            
            for post in unsent_posts:
                try:
                    success = self.whatsapp.send_trump_post_notification(post)
                    
                    if success:
                        self.db.mark_notification_sent(
                            post['post_id'], 
                            post['platform'], 
                            "sent"
                        )
                        logger.info(f"Notification sent for post {post['post_id']}")
                    else:
                        self.db.mark_notification_sent(
                            post['post_id'], 
                            post['platform'], 
                            "failed", 
                            "WhatsApp send failed"
                        )
                        logger.error(f"Failed to send notification for post {post['post_id']}")
                    
                    # Add delay between notifications to avoid rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing notification for post {post['post_id']}: {e}")
                    self.db.mark_notification_sent(
                        post['post_id'], 
                        post['platform'], 
                        "error", 
                        str(e)
                    )
                    
        except Exception as e:
            logger.error(f"Error processing pending notifications: {e}")
    
    async def send_startup_notification(self):
        """Send notification when service starts"""
        try:
            platform_status = self.social_aggregator.get_platform_status()
            
            message = "🚀 Trump Monitor Service Started!\n\n"
            message += "📱 Platform Status:\n"
            
            for platform, status in platform_status.items():
                status_emoji = "✅" if status else "❌"
                message += f"  {status_emoji} {platform}\n"
            
            message += f"\n⏰ Check interval: {Config.CHECK_INTERVAL_MINUTES} minutes"
            
            self.whatsapp.send_system_notification(message)
            
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
    
    async def send_shutdown_notification(self):
        """Send notification when service stops"""
        try:
            message = "🛑 Trump Monitor Service Stopped\n\n"
            message += f"Last check: {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_check_time else 'Never'}"
            
            self.whatsapp.send_system_notification(message)
            
        except Exception as e:
            logger.error(f"Error sending shutdown notification: {e}")
    
    async def send_daily_summary(self):
        """Send daily summary of activity"""
        try:
            stats = self.db.get_statistics()
            self.whatsapp.send_daily_summary(stats)
            logger.info("Daily summary sent")
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
    
    async def manual_check(self) -> Dict[str, Any]:
        """Manually trigger a check for new posts"""
        logger.info("Manual post check triggered")
        
        try:
            await self.check_for_new_posts()
            await self.process_pending_notifications()
            
            stats = self.db.get_statistics()
            return {
                "status": "success",
                "message": "Manual check completed",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Manual check failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        try:
            platform_status = self.social_aggregator.get_platform_status()
            stats = self.db.get_statistics()
            
            return {
                "is_running": self.is_running,
                "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
                "check_interval_minutes": Config.CHECK_INTERVAL_MINUTES,
                "platform_status": platform_status,
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                "is_running": self.is_running,
                "error": str(e)
            }
    
    async def run_forever(self):
        """Run the service indefinitely"""
        if not await self.start_monitoring():
            logger.error("Failed to start monitoring service")
            return
        
        try:
            logger.info("Trump Monitor Service running. Press Ctrl+C to stop.")
            
            # Keep the service running
            while self.is_running:
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            await self.stop_monitoring()

# Global service instance
monitor_service = None

async def get_monitor_service() -> TrumpMonitorService:
    """Get or create the monitor service instance"""
    global monitor_service
    if monitor_service is None:
        monitor_service = TrumpMonitorService()
    return monitor_service