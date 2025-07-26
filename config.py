import os
from decouple import config
from typing import Optional

class Config:
    """Configuration class for Trump Monitor WhatsApp Client"""
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = config('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN: str = config('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER: str = config('TWILIO_WHATSAPP_NUMBER', default='whatsapp:+14155238886')
    YOUR_WHATSAPP_NUMBER: str = config('YOUR_WHATSAPP_NUMBER')
    
    # Twitter/X API Configuration
    TWITTER_BEARER_TOKEN: Optional[str] = config('TWITTER_BEARER_TOKEN', default=None)
    
    # Truth Social API Configuration
    TRUTH_SOCIAL_API_KEY: Optional[str] = config('TRUTH_SOCIAL_API_KEY', default=None)
    TRUTH_SOCIAL_API_BASE_URL: str = config('TRUTH_SOCIAL_API_BASE_URL', 
                                          default='https://api.scrapecreators.com/v1/truthsocial')
    
    # Monitoring Configuration
    CHECK_INTERVAL_MINUTES: int = config('CHECK_INTERVAL_MINUTES', default=5, cast=int)
    MAX_POSTS_PER_CHECK: int = config('MAX_POSTS_PER_CHECK', default=50, cast=int)
    
    # Database Configuration
    DATABASE_PATH: str = config('DATABASE_PATH', default='trump_monitor.db')
    
    # Logging Configuration
    LOG_LEVEL: str = config('LOG_LEVEL', default='INFO')
    LOG_FILE: str = config('LOG_FILE', default='trump_monitor.log')
    
    # Trump's social media handles
    TRUMP_TWITTER_HANDLE: str = "realDonaldTrump"
    TRUMP_TRUTH_SOCIAL_HANDLE: str = "realDonaldTrump"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        required_configs = [
            cls.TWILIO_ACCOUNT_SID,
            cls.TWILIO_AUTH_TOKEN,
            cls.YOUR_WHATSAPP_NUMBER
        ]
        
        missing_configs = [config for config in required_configs if not config]
        
        if missing_configs:
            print(f"Missing required configuration: {missing_configs}")
            return False
            
        return True