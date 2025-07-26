#!/usr/bin/env python3
"""
Trump Monitor WhatsApp Client
Main entry point for the monitoring service

Usage:
    python main.py                    # Run standalone service
    python main.py --api             # Run with FastAPI web interface
    python main.py --test            # Test configuration and connections
    python main.py --manual-check    # Run a manual check once
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from config import Config
from monitor_service import TrumpMonitorService, get_monitor_service

logger = logging.getLogger(__name__)

async def test_configuration():
    """Test configuration and connections"""
    print("🧪 Testing Trump Monitor Configuration...\n")
    
    # Test configuration
    print("📋 Configuration Validation:")
    if Config.validate_config():
        print("  ✅ Configuration is valid")
    else:
        print("  ❌ Configuration validation failed")
        return False
    
    try:
        # Test database
        print("\n💾 Database Test:")
        from database import DatabaseManager
        db = DatabaseManager()
        print("  ✅ Database connection successful")
        
        # Test WhatsApp
        print("\n📱 WhatsApp Test:")
        from whatsapp_client import WhatsAppClient
        whatsapp = WhatsAppClient()
        if whatsapp.test_connection():
            print("  ✅ WhatsApp connection successful")
        else:
            print("  ❌ WhatsApp connection failed")
            return False
        
        # Test social media monitors
        print("\n🌐 Social Media Monitors Test:")
        from social_media_monitors import SocialMediaAggregator
        aggregator = SocialMediaAggregator()
        
        platform_status = aggregator.get_platform_status()
        for platform, status in platform_status.items():
            status_emoji = "✅" if status else "❌"
            print(f"  {status_emoji} {platform}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

async def run_manual_check():
    """Run a single manual check"""
    print("🔍 Running manual check for new Trump posts...\n")
    
    try:
        service = await get_monitor_service()
        result = await service.manual_check()
        
        if result["status"] == "success":
            print("✅ Manual check completed successfully!")
            stats = result.get("stats", {})
            
            if stats:
                print("\n📊 Statistics:")
                platform_stats = stats.get('platform_stats', {})
                for platform, count in platform_stats.items():
                    print(f"  • {platform}: {count} total posts")
                
                print(f"  • Notifications sent: {stats.get('notifications_sent', 0)}")
        else:
            print(f"❌ Manual check failed: {result['message']}")
            
    except Exception as e:
        print(f"❌ Manual check error: {e}")

async def run_standalone_service():
    """Run the monitoring service standalone"""
    print("🚀 Starting Trump Monitor Service (Standalone Mode)")
    print("Press Ctrl+C to stop the service\n")
    
    try:
        service = await get_monitor_service()
        await service.run_forever()
        
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")
    except Exception as e:
        print(f"\n❌ Service error: {e}")
        logger.error(f"Service error: {e}")

def run_api_service():
    """Run the service with FastAPI web interface"""
    print("🌐 Starting Trump Monitor Service with Web API")
    print("Web interface will be available at http://localhost:8000\n")
    
    try:
        import uvicorn
        from api_server import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except ImportError:
        print("❌ FastAPI/Uvicorn not installed. Install with: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ API server error: {e}")
        logger.error(f"API server error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Trump Monitor WhatsApp Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run standalone monitoring service
  python main.py --api             # Run with web API interface
  python main.py --test            # Test configuration and connections
  python main.py --manual-check    # Run a single manual check
        """
    )
    
    parser.add_argument(
        '--api',
        action='store_true',
        help='Run with FastAPI web interface'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test configuration and connections'
    )
    
    parser.add_argument(
        '--manual-check',
        action='store_true',
        help='Run a single manual check'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Trump Monitor v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 60)
    print("🇺🇸 TRUMP MONITOR WHATSAPP CLIENT 🇺🇸")
    print("=" * 60)
    print()
    
    # Handle different modes
    if args.test:
        success = asyncio.run(test_configuration())
        sys.exit(0 if success else 1)
    
    elif args.manual_check:
        asyncio.run(run_manual_check())
        sys.exit(0)
    
    elif args.api:
        run_api_service()
    
    else:
        # Default: standalone service
        asyncio.run(run_standalone_service())

if __name__ == "__main__":
    main()