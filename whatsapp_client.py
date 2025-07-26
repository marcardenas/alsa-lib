import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class WhatsAppClient:
    """WhatsApp client for sending notifications via Twilio"""
    
    def __init__(self):
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.from_number = Config.TWILIO_WHATSAPP_NUMBER
        self.to_number = Config.YOUR_WHATSAPP_NUMBER
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("WhatsApp client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp client: {e}")
            raise
    
    def send_message(self, message: str, media_url: Optional[str] = None) -> bool:
        """Send a WhatsApp message"""
        try:
            message_kwargs = {
                'body': message,
                'from_': self.from_number,
                'to': self.to_number
            }
            
            # Add media if provided
            if media_url:
                message_kwargs['media_url'] = [media_url]
            
            message_obj = self.client.messages.create(**message_kwargs)
            
            logger.info(f"WhatsApp message sent successfully. SID: {message_obj.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Twilio error sending WhatsApp message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {e}")
            return False
    
    def send_trump_post_notification(self, post_data: Dict[str, Any]) -> bool:
        """Send a notification about a new Trump post"""
        try:
            platform = post_data.get('platform', 'Unknown')
            content = post_data.get('content', 'No content')
            created_at = post_data.get('created_at', 'Unknown time')
            url = post_data.get('url', '')
            
            # Truncate content if too long
            if len(content) > 200:
                content = content[:200] + "..."
            
            # Format the message
            message = f"🚨 NEW {platform.upper()} POST FROM TRUMP!\n\n"
            message += f"📅 {created_at}\n\n"
            message += f"📝 {content}\n\n"
            
            if url:
                message += f"🔗 {url}"
            
            # Extract media URLs if available
            media_urls = post_data.get('media_urls')
            media_url = None
            if media_urls:
                try:
                    # Try to parse media URLs (could be JSON string or list)
                    import json
                    if isinstance(media_urls, str):
                        media_list = json.loads(media_urls)
                    else:
                        media_list = media_urls
                    
                    if media_list and len(media_list) > 0:
                        media_url = media_list[0]  # Use first media item
                except:
                    pass
            
            return self.send_message(message, media_url)
            
        except Exception as e:
            logger.error(f"Error formatting Trump post notification: {e}")
            return False
    
    def send_system_notification(self, message: str) -> bool:
        """Send a system notification (errors, status updates, etc.)"""
        try:
            system_message = f"🤖 TRUMP MONITOR SYSTEM\n\n{message}"
            return self.send_message(system_message)
        except Exception as e:
            logger.error(f"Error sending system notification: {e}")
            return False
    
    def send_daily_summary(self, stats: Dict[str, Any]) -> bool:
        """Send a daily summary of monitoring activity"""
        try:
            message = "📊 DAILY TRUMP MONITOR SUMMARY\n\n"
            
            platform_stats = stats.get('platform_stats', {})
            if platform_stats:
                message += "📱 Posts by Platform:\n"
                for platform, count in platform_stats.items():
                    message += f"  • {platform}: {count} posts\n"
                message += "\n"
            
            notifications_sent = stats.get('notifications_sent', 0)
            message += f"📤 Notifications sent: {notifications_sent}\n\n"
            
            recent_activity = stats.get('recent_activity', [])
            if recent_activity:
                message += "🔍 Recent Activity (24h):\n"
                for activity in recent_activity:
                    platform = activity.get('platform', 'Unknown')
                    checks = activity.get('checks', 0)
                    new_posts = activity.get('total_new_posts', 0)
                    message += f"  • {platform}: {checks} checks, {new_posts} new posts\n"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test the WhatsApp connection"""
        try:
            test_message = "🧪 Trump Monitor WhatsApp Client Test\n\nThis is a test message to verify the connection is working properly."
            return self.send_message(test_message)
        except Exception as e:
            logger.error(f"WhatsApp connection test failed: {e}")
            return False