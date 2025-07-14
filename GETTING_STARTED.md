# Getting Started with TikTok AI Video Bot

This guide will help you set up and start using the TikTok AI Video Bot to automatically generate and post videos to TikTok.

## 📋 Prerequisites

- **Python 3.9+** - [Download Python](https://python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **FFmpeg** - [Download FFmpeg](https://ffmpeg.org/download.html)
- **AI Service API Key** - Get from [AI/ML API](https://aimlapi.com) or other providers

## 🚀 Quick Installation

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/tiktok-ai-bot.git
cd tiktok-ai-bot

# Run the installation script
./install.sh
```

### Option 2: Manual Installation

```bash
# Clone and enter directory
git clone https://github.com/your-username/tiktok-ai-bot.git
cd tiktok-ai-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install

# Install browser dependencies
python -m playwright install

# Create directories
mkdir -p generated_videos video_queue logs config data cookies

# Copy environment template
cp .env.example .env
```

## ⚙️ Configuration

### 1. API Keys Setup

Edit the `.env` file with your API keys:

```env
# AI Video Generation (Required)
AIML_API_KEY=your_aiml_api_key_here

# OpenAI for enhanced content (Optional but recommended)
OPENAI_API_KEY=your_openai_api_key_here

# TikTok Account
TIKTOK_USERNAME=your_tiktok_username
```

#### Getting API Keys:

**AI/ML API (Recommended - supports multiple AI services):**
1. Visit [aimlapi.com](https://aimlapi.com)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add to `.env` file as `AIML_API_KEY`

**OpenAI API (Optional for better content):**
1. Visit [platform.openai.com](https://platform.openai.com)
2. Create an account and get API key
3. Add to `.env` file as `OPENAI_API_KEY`

### 2. TikTok Account Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Add your TikTok account
python main.py add-account
```

Follow the prompts to:
1. Enter your TikTok username
2. Provide path to cookies file (see Cookie Setup below)

#### Cookie Setup:

1. **Install Browser Extension:**
   - Chrome: [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Extract Cookies:**
   - Log in to TikTok in your browser
   - Click the extension icon
   - Export cookies to `cookies/tiktok_cookies.txt`

## 🎬 First Video Generation

### Test the Setup

```bash
# Run quick start example
python examples/quick_start.py
```

### Generate Your First Video

```bash
# Generate a single video
python main.py generate --theme motivational --post-now
```

### Available Themes:
- `motivational` - Inspirational content
- `educational` - Learning and facts
- `trending` - Current trends
- `abstract` - Artistic visuals
- `nature` - Natural scenes
- `urban` - City lifestyle

## 🤖 Automated Posting

### Start the Scheduler

```bash
# Start automated daily posting
python main.py start-scheduler
```

This will:
- Post videos at optimal times (9 AM, 3 PM, 9 PM by default)
- Maintain a queue of videos
- Generate new content automatically

### Populate the Queue

```bash
# Generate 10 videos for the queue
python main.py generate-queue --count 10
```

## 📊 Monitoring and Management

### Check Status

```bash
# View bot statistics
python main.py show-stats

# Check video queue
python main.py show-queue

# List TikTok accounts
python main.py list-accounts

# Health check
python main.py health-check
```

### View Logs

```bash
# Real-time logs
tail -f logs/tiktok_bot.log

# Error logs
tail -f logs/errors.log
```

## 🛠️ Customization

### Custom Content Themes

```bash
# Setup custom themes
python main.py setup-themes
```

### Posting Schedule

Edit `.env` file:

```env
# Post times (24-hour format)
OPTIMAL_POST_TIMES=09:00,15:00,21:00

# Daily post count
DAILY_POST_COUNT=3

# Content queue size
CONTENT_QUEUE_SIZE=20
```

### Content Settings

```env
# Video settings
DEFAULT_VIDEO_DURATION=10
ASPECT_RATIO=9:16
VIDEO_QUALITY=1080p

# Safety settings
MAX_DAILY_UPLOADS=5
ENABLE_HUMANLIKE_BEHAVIOR=true
```

## 🚨 Troubleshooting

### Common Issues

1. **"No AI services available"**
   - Check your API keys in `.env`
   - Verify API key validity
   - Ensure you have credits/quota

2. **"TikTok upload failed"**
   - Check cookies file is valid and recent
   - Re-export cookies from browser
   - Verify account isn't banned/restricted

3. **"Browser installation failed"**
   ```bash
   python -m playwright install --force
   ```

4. **"FFmpeg not found"**
   - Install FFmpeg for your OS
   - Add to PATH environment variable

### Debug Mode

Enable debug logging:

```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

### Test Individual Components

```bash
# Test AI video generation
python main.py test-generation --service aiml

# Test TikTok upload (dry run)
DRY_RUN=true python main.py post-now
```

## 📚 Advanced Usage

### API Integration

```python
from src.bot import TikTokBot
import asyncio

async def custom_workflow():
    async with TikTokBot() as bot:
        # Generate video
        video = await bot.generate_video(theme="educational")
        
        # Custom scheduling
        import datetime
        schedule_time = datetime.datetime.now() + datetime.timedelta(hours=2)
        
        # Post with custom settings
        result = await bot.post_video(
            video_path=video,
            caption="Custom caption! #educational",
            schedule_time=schedule_time
        )
        
        return result

# Run
asyncio.run(custom_workflow())
```

### Multi-Account Management

```bash
# Add multiple accounts
python main.py add-account  # Account 1
python main.py add-account  # Account 2

# Use specific account
TIKTOK_USERNAME=account2 python main.py generate --post-now
```

### Content Calendar

```bash
# Create 7-day content calendar
python main.py create-calendar --days 7
```

## 🔒 Security & Best Practices

1. **API Key Security:**
   - Never commit `.env` to version control
   - Use environment variables in production
   - Regularly rotate API keys

2. **Rate Limiting:**
   - Default: 5 uploads per day maximum
   - Randomized delays between actions
   - Human-like behavior patterns

3. **Account Safety:**
   - Use fresh, dedicated accounts
   - Don't exceed TikTok's limits
   - Monitor for unusual activity

4. **Content Compliance:**
   - Review generated content
   - Ensure compliance with TikTok guidelines
   - Use copyright checking features

## 🆘 Support

- 📚 **Documentation:** [Full Documentation](docs/)
- 🐛 **Issues:** [GitHub Issues](https://github.com/your-username/tiktok-ai-bot/issues)
- 💬 **Discord:** [Join Community](https://discord.gg/your-server)
- 📧 **Email:** support@tiktok-ai-bot.com

## 🚀 Next Steps

1. **Scale Up:** Add more TikTok accounts
2. **Optimize:** Analyze performance and adjust themes
3. **Customize:** Create custom content templates
4. **Integrate:** Connect with other social platforms
5. **Monitor:** Set up alerts and analytics

---

Happy TikTok botting! 🎉