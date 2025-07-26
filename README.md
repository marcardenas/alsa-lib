# 🇺🇸 Trump Monitor WhatsApp Client

A comprehensive monitoring system that tracks Donald Trump's posts on Truth Social and Twitter/X, then sends real-time WhatsApp notifications whenever he makes a new post.

## 🚀 Features

- **Multi-Platform Monitoring**: Monitors both Truth Social and Twitter/X
- **Real-Time Notifications**: Instant WhatsApp alerts for new posts
- **Duplicate Detection**: Prevents duplicate notifications using content hashing
- **Web Dashboard**: Optional web interface for monitoring and management
- **Persistent Storage**: SQLite database for tracking posts and notifications
- **Automatic Scheduling**: Configurable check intervals (default: 5 minutes)
- **Daily Summaries**: Automated daily activity reports
- **Error Handling**: Robust error handling and logging

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **Twilio Account** with WhatsApp Business API access
3. **Truth Social API Key** (optional - has fallback scraping)
4. **Twitter API Bearer Token** (optional - free tier very limited)

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd trump-monitor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your credentials:

```env
# Twilio Configuration (REQUIRED)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+1234567890

# Twitter/X API Configuration (OPTIONAL)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Truth Social API (OPTIONAL)
TRUTH_SOCIAL_API_KEY=your_scrapecreators_api_key

# Monitoring Configuration
CHECK_INTERVAL_MINUTES=5
MAX_POSTS_PER_CHECK=50
```

## 🔧 Setup Guide

### Twilio Setup (Required)

1. **Create Twilio Account**: Sign up at [twilio.com](https://www.twilio.com)
2. **Get Credentials**: Find your Account SID and Auth Token in the Twilio Console
3. **Set Up WhatsApp Sandbox**:
   - Go to Messaging → Try it out → Send a WhatsApp message
   - Note the sandbox number (usually +14155238886)
   - Send the join code from your phone to activate
4. **Configure Webhook** (if using API mode):
   - Set webhook URL to your server + `/message`

### Truth Social API Setup (Optional)

1. **ScrapeCreators API**: Sign up at [scrapecreators.com](https://scrapecreators.com)
2. **Get API Key**: Generate an API key for Truth Social access
3. **Add to .env**: Set `TRUTH_SOCIAL_API_KEY` in your environment file

*Note: Without API key, the system will attempt basic scraping (limited functionality)*

### Twitter API Setup (Optional)

1. **Developer Account**: Apply at [developer.x.com](https://developer.x.com)
2. **Create Project**: Set up a new project and app
3. **Generate Bearer Token**: Create a Bearer Token for API access
4. **Add to .env**: Set `TWITTER_BEARER_TOKEN` in your environment file

*Note: Free tier is very limited (100 tweets/month)*

## 🚀 Usage

### Test Configuration

Before running, test your setup:

```bash
python main.py --test
```

This will verify:
- ✅ Configuration validity
- ✅ Database connection
- ✅ WhatsApp connection
- ✅ Social media API access

### Run Standalone Service

Start the monitoring service:

```bash
python main.py
```

The service will:
- Check for new posts every 5 minutes (configurable)
- Send WhatsApp notifications for new posts
- Send daily summaries
- Log all activity

### Run with Web Interface

Start with a web dashboard:

```bash
python main.py --api
```

Then visit: `http://localhost:8000`

The web interface provides:
- Real-time service status
- Platform connectivity status
- Recent posts view
- Manual check trigger
- Statistics dashboard

### Manual Check

Run a one-time check:

```bash
python main.py --manual-check
```

## 📱 WhatsApp Notifications

You'll receive notifications for:

### New Posts
```
🚨 NEW TRUTH SOCIAL POST FROM TRUMP!

📅 2024-01-15 14:30:00

📝 This is the content of Trump's post...

🔗 https://truthsocial.com/@realDonaldTrump/12345
```

### System Status
```
🤖 TRUMP MONITOR SYSTEM

🚀 Service started successfully!
Platform Status:
  ✅ Truth Social
  ❌ Twitter/X

⏰ Check interval: 5 minutes
```

### Daily Summaries
```
📊 DAILY TRUMP MONITOR SUMMARY

📱 Posts by Platform:
  • Truth Social: 15 posts
  • Twitter/X: 3 posts

📤 Notifications sent: 18

🔍 Recent Activity (24h):
  • Truth Social: 288 checks, 15 new posts
  • Twitter/X: 288 checks, 3 new posts
```

## 🔧 Configuration Options

Edit your `.env` file to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `CHECK_INTERVAL_MINUTES` | How often to check for new posts | 5 |
| `MAX_POSTS_PER_CHECK` | Maximum posts to fetch per check | 50 |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `DATABASE_PATH` | SQLite database file path | trump_monitor.db |

## 📊 Web API Endpoints

When running with `--api`, these endpoints are available:

- `GET /` - Web dashboard
- `GET /status` - Service status
- `POST /manual-check` - Trigger manual check
- `GET /posts/recent` - Recent posts
- `GET /statistics` - Monitoring statistics
- `POST /start` - Start monitoring
- `POST /stop` - Stop monitoring
- `GET /health` - Health check

## 🗄️ Database Schema

The system uses SQLite with these tables:

- **posts**: Stores all discovered posts
- **notifications**: Tracks sent notifications
- **monitoring_log**: Logs all monitoring activity

## 🔍 Troubleshooting

### Common Issues

**WhatsApp messages not sending:**
- Verify Twilio credentials in `.env`
- Check WhatsApp sandbox is activated
- Ensure phone number format is correct (`whatsapp:+1234567890`)

**No posts being found:**
- Check API credentials for Truth Social/Twitter
- Verify internet connection
- Check logs for API errors

**Service stops unexpectedly:**
- Check log files for errors
- Verify all dependencies are installed
- Ensure sufficient system resources

### Checking Logs

View logs in real-time:
```bash
tail -f trump_monitor.log
```

### Manual Database Check

Inspect the database:
```bash
sqlite3 trump_monitor.db
.tables
SELECT * FROM posts LIMIT 10;
```

## 🔒 Security Notes

1. **Keep credentials secure**: Never commit `.env` files to version control
2. **Use environment variables**: In production, use proper environment variable management
3. **Regular updates**: Keep dependencies updated for security patches
4. **Network security**: Use HTTPS for webhook endpoints
5. **Rate limiting**: Respect API rate limits to avoid being blocked

## 📈 Performance Tips

1. **Adjust check intervals**: Increase `CHECK_INTERVAL_MINUTES` for less frequent checks
2. **Limit post fetching**: Reduce `MAX_POSTS_PER_CHECK` if experiencing slowdowns
3. **Database maintenance**: Periodically clean old posts if storage is a concern
4. **Monitor resources**: Keep an eye on CPU and memory usage

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional social media platforms
- Enhanced scraping methods
- Better error recovery
- Mobile app interface
- Advanced filtering options

## ⚠️ Legal Disclaimer

This tool is for educational and personal use only. Users are responsible for:

- Complying with platform Terms of Service
- Respecting rate limits and API usage policies
- Following applicable laws and regulations
- Using responsibly and ethically

## 📄 License

This project is provided as-is for educational purposes. Use at your own risk and responsibility.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review log files for errors
3. Test configuration with `python main.py --test`
4. Ensure all prerequisites are met

---

**Made with ❤️ for keeping track of important social media activity**
