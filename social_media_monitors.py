import requests
import logging
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from config import Config

logger = logging.getLogger(__name__)

class SocialMediaMonitor(ABC):
    """Abstract base class for social media monitors"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.last_check = None
    
    @abstractmethod
    def fetch_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent posts from the platform"""
        pass
    
    def normalize_post_data(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize post data to a standard format"""
        return {
            'post_id': raw_post.get('id', ''),
            'platform': self.platform_name,
            'content': raw_post.get('content', ''),
            'created_at': raw_post.get('created_at', ''),
            'url': raw_post.get('url', ''),
            'media_urls': json.dumps(raw_post.get('media_urls', [])),
            'engagement_metrics': json.dumps(raw_post.get('engagement_metrics', {}))
        }

class TruthSocialMonitor(SocialMediaMonitor):
    """Monitor for Truth Social posts"""
    
    def __init__(self):
        super().__init__("Truth Social")
        self.api_key = Config.TRUTH_SOCIAL_API_KEY
        self.base_url = Config.TRUTH_SOCIAL_API_BASE_URL
        self.username = Config.TRUMP_TRUTH_SOCIAL_HANDLE
        
        if not self.api_key:
            logger.warning("Truth Social API key not configured - using fallback scraping method")
    
    def fetch_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch posts from Truth Social"""
        posts = []
        
        if self.api_key:
            posts = self._fetch_via_api(limit)
        else:
            posts = self._fetch_via_scraping(limit)
        
        return posts
    
    def _fetch_via_api(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch posts using ScrapeCreators API"""
        try:
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            params = {
                'handle': self.username,
                'limit': min(limit, 100)  # API typically limits to 100
            }
            
            response = requests.get(
                f"{self.base_url}/profile",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for post in data.get('posts', []):
                    normalized_post = {
                        'id': post.get('id', ''),
                        'content': post.get('content', ''),
                        'created_at': post.get('created_at', ''),
                        'url': f"https://truthsocial.com/@{self.username}/{post.get('id', '')}",
                        'media_urls': post.get('media', []),
                        'engagement_metrics': {
                            'likes': post.get('favourites_count', 0),
                            'reposts': post.get('reblogs_count', 0),
                            'replies': post.get('replies_count', 0)
                        }
                    }
                    posts.append(self.normalize_post_data(normalized_post))
                
                logger.info(f"Fetched {len(posts)} posts from Truth Social API")
                return posts
            else:
                logger.error(f"Truth Social API error: {response.status_code} - {response.text}")
                
        except requests.RequestException as e:
            logger.error(f"Truth Social API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching Truth Social posts: {e}")
        
        return []
    
    def _fetch_via_scraping(self, limit: int) -> List[Dict[str, Any]]:
        """Fallback scraping method for Truth Social"""
        try:
            # This is a simplified scraping approach
            # In practice, you might need more sophisticated scraping
            logger.info("Attempting to scrape Truth Social posts (fallback method)")
            
            # Try to fetch from the public archive site
            archive_url = f"https://trumpstruth.org/"
            
            response = requests.get(archive_url, timeout=30)
            if response.status_code == 200:
                # This would require parsing HTML - simplified for demo
                logger.info("Successfully connected to Truth Social archive")
                # For now, return empty list - would need proper HTML parsing
                return []
            else:
                logger.error(f"Failed to access Truth Social archive: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Truth Social scraping failed: {e}")
        
        return []

class TwitterMonitor(SocialMediaMonitor):
    """Monitor for Twitter/X posts"""
    
    def __init__(self):
        super().__init__("Twitter/X")
        self.bearer_token = Config.TWITTER_BEARER_TOKEN
        self.username = Config.TRUMP_TWITTER_HANDLE
        self.base_url = "https://api.x.com/2"
        
        if not self.bearer_token:
            logger.warning("Twitter Bearer Token not configured - Twitter monitoring disabled")
    
    def fetch_posts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch posts from Twitter/X"""
        if not self.bearer_token:
            logger.warning("Twitter monitoring skipped - no bearer token")
            return []
        
        posts = []
        
        try:
            # First get user ID
            user_id = self._get_user_id()
            if not user_id:
                logger.error("Could not get Trump's Twitter user ID")
                return []
            
            # Then get user's tweets
            posts = self._fetch_user_tweets(user_id, limit)
            
        except Exception as e:
            logger.error(f"Error fetching Twitter posts: {e}")
        
        return posts
    
    def _get_user_id(self) -> Optional[str]:
        """Get user ID from username"""
        try:
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/users/by/username/{self.username}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('data', {}).get('id')
                logger.info(f"Retrieved Twitter user ID: {user_id}")
                return user_id
            else:
                logger.error(f"Twitter API error getting user ID: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error getting Twitter user ID: {e}")
        
        return None
    
    def _fetch_user_tweets(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch user's tweets"""
        try:
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'max_results': min(limit, 100),  # Twitter API limit
                'tweet.fields': 'created_at,public_metrics,attachments',
                'media.fields': 'url,preview_image_url',
                'expansions': 'attachments.media_keys'
            }
            
            response = requests.get(
                f"{self.base_url}/users/{user_id}/tweets",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                # Get media information if available
                media_dict = {}
                if 'includes' in data and 'media' in data['includes']:
                    for media in data['includes']['media']:
                        media_dict[media['media_key']] = media
                
                for tweet in data.get('data', []):
                    # Extract media URLs
                    media_urls = []
                    if 'attachments' in tweet and 'media_keys' in tweet['attachments']:
                        for media_key in tweet['attachments']['media_keys']:
                            if media_key in media_dict:
                                media_info = media_dict[media_key]
                                if 'url' in media_info:
                                    media_urls.append(media_info['url'])
                                elif 'preview_image_url' in media_info:
                                    media_urls.append(media_info['preview_image_url'])
                    
                    normalized_post = {
                        'id': tweet.get('id', ''),
                        'content': tweet.get('text', ''),
                        'created_at': tweet.get('created_at', ''),
                        'url': f"https://twitter.com/{self.username}/status/{tweet.get('id', '')}",
                        'media_urls': media_urls,
                        'engagement_metrics': tweet.get('public_metrics', {})
                    }
                    posts.append(self.normalize_post_data(normalized_post))
                
                logger.info(f"Fetched {len(posts)} posts from Twitter")
                return posts
            else:
                logger.error(f"Twitter API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error fetching Twitter posts: {e}")
        
        return []

class SocialMediaAggregator:
    """Aggregates posts from multiple social media monitors"""
    
    def __init__(self):
        self.monitors = []
        
        # Initialize available monitors
        if Config.TRUTH_SOCIAL_API_KEY or True:  # Always try Truth Social (has fallback)
            self.monitors.append(TruthSocialMonitor())
        
        if Config.TWITTER_BEARER_TOKEN:
            self.monitors.append(TwitterMonitor())
        
        logger.info(f"Initialized {len(self.monitors)} social media monitors")
    
    def fetch_all_posts(self, limit_per_platform: int = 25) -> List[Dict[str, Any]]:
        """Fetch posts from all configured platforms"""
        all_posts = []
        
        for monitor in self.monitors:
            try:
                logger.info(f"Fetching posts from {monitor.platform_name}")
                posts = monitor.fetch_posts(limit_per_platform)
                all_posts.extend(posts)
                logger.info(f"Retrieved {len(posts)} posts from {monitor.platform_name}")
                
                # Add small delay between API calls
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching from {monitor.platform_name}: {e}")
        
        # Sort posts by creation date (newest first)
        all_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        logger.info(f"Total posts retrieved: {len(all_posts)}")
        return all_posts
    
    def get_platform_status(self) -> Dict[str, bool]:
        """Get status of all platforms"""
        status = {}
        for monitor in self.monitors:
            try:
                # Try a small fetch to test connectivity
                posts = monitor.fetch_posts(1)
                status[monitor.platform_name] = True
            except:
                status[monitor.platform_name] = False
        
        return status