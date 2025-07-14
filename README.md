# TikTok AI Video Bot 🤖🎥

An automated TikTok bot that creates videos using AI video generation services and posts them daily with intelligent scheduling, hashtag optimization, and content management.

## Features ✨

- **🎬 AI Video Generation**: Integrates with multiple AI video services (Runway, Pika, Kling, etc.)
- **📅 Smart Scheduling**: Automated daily posting with optimal timing
- **🏷️ Hashtag Optimization**: Automatic trending hashtag detection and inclusion
- **🔄 Content Management**: Queue system for generated videos
- **📊 Analytics Tracking**: Monitor performance and engagement
- **🚀 Multi-Account Support**: Manage multiple TikTok accounts
- **🧠 Content Themes**: Customizable content categories and styles
- **🔐 Secure Authentication**: Cookie-based TikTok authentication
- **📱 Captcha Handling**: Automatic captcha solving
- **🎵 Sound Integration**: Add trending TikTok sounds

## Supported AI Video Services

- **Runway Gen-4 Turbo** - High-quality, fast generation
- **Pika 2.2** - Text-to-video with effects
- **Kling AI** - Professional video generation
- **MiniMax Hailuo** - Creative video styles
- **ByteDance Seedance** - Image-to-video animation
- **Google Veo** - Advanced video synthesis
- **Luma Dream Machine** - Cinematic generations

## Installation 🛠️

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/tiktok-ai-bot.git
cd tiktok-ai-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install system dependencies:**
```bash
# Install Node.js dependencies for TikTok automation
npm install

# Install Playwright browsers
python -m playwright install
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

## Configuration ⚙️

### Environment Variables

Create a `.env` file with the following:

```env
# AI Video Service APIs
RUNWAY_API_KEY=your_runway_key
PIKA_API_KEY=your_pika_key
KLING_API_KEY=your_kling_key
MINIMAX_API_KEY=your_minimax_key

# AI/ML API (unified access)
AIML_API_KEY=your_aiml_api_key

# Content Settings
DEFAULT_VIDEO_DURATION=10
DAILY_POST_COUNT=3
OPTIMAL_POST_TIMES=09:00,15:00,21:00

# Storage
VIDEOS_DIR=./generated_videos
QUEUE_DIR=./video_queue

# Analytics
ENABLE_ANALYTICS=true
```

### Account Setup

1. **Add TikTok accounts:**
```bash
python main.py --add-account
```

2. **Configure content themes:**
```bash
python main.py --setup-themes
```

## Usage 🚀

### Quick Start

```bash
# Generate and post a single video
python main.py --generate-and-post

# Start daily automation
python main.py --start-scheduler

# Generate videos for queue
python main.py --generate-queue --count 10
```

### Advanced Usage

```python
from tiktok_bot import TikTokBot

# Initialize bot
bot = TikTokBot()

# Add account
bot.add_account("username", cookies_file="cookies.txt")

# Generate video with specific theme
video = await bot.generate_video(
    theme="motivational",
    style="cinematic",
    duration=10
)

# Post with custom settings
await bot.post_video(
    video_path=video,
    caption="Daily motivation! #motivation #success",
    hashtags=["#viral", "#fyp"],
    schedule_time="15:00"
)
```

## Project Structure 📁

```
tiktok-ai-bot/
├── src/
│   ├── ai_services/         # AI video generation integrations
│   ├── tiktok/             # TikTok automation
│   ├── content/            # Content management
│   ├── scheduler/          # Posting scheduler
│   └── analytics/          # Performance tracking
├── config/                 # Configuration files
├── data/                  # Generated content storage
├── logs/                  # Application logs
└── scripts/               # Utility scripts
```

## Content Themes 🎨

The bot supports various content themes:

- **Motivational Quotes** - Inspiring text with dynamic visuals
- **Educational Content** - Quick facts and tips
- **Trending Topics** - Current events and viral themes
- **Product Showcases** - Commercial content
- **Abstract Art** - Creative visual content
- **Nature Scenes** - Calming landscapes
- **Urban Life** - City scenes and lifestyle

## Automation Features 🤖

### Daily Scheduling
- Automatic video generation based on queue status
- Optimal posting times based on audience analytics
- Failure handling and retry mechanisms

### Content Intelligence
- Trending hashtag detection
- Audience engagement analysis
- Content performance optimization

### Safety Features
- Rate limiting to avoid account restrictions
- Human-like posting patterns
- Error handling and logging

## API Documentation 📚

### Core Classes

#### TikTokBot
Main bot controller handling all operations.

```python
class TikTokBot:
    async def generate_video(theme, style, duration)
    async def post_video(video_path, caption, hashtags)
    async def schedule_posts(schedule)
    def add_account(username, cookies)
```

#### AIVideoGenerator
Manages AI video generation services.

```python
class AIVideoGenerator:
    async def generate_runway(prompt, duration)
    async def generate_pika(prompt, style)
    async def generate_kling(prompt, aspect_ratio)
```

#### ContentManager
Handles content themes and queue management.

```python
class ContentManager:
    def create_theme_prompt(theme)
    def add_to_queue(video_info)
    def get_next_video()
```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer ⚠️

This bot is for educational and personal use only. Please ensure compliance with TikTok's Terms of Service and your local laws. The authors are not responsible for any misuse of this software.

## Support 💬

- 📧 Email: support@tiktok-ai-bot.com
- 💬 Discord: [Join our server](https://discord.gg/your-server)
- 📖 Documentation: [Full docs](https://docs.tiktok-ai-bot.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/tiktok-ai-bot/issues)

## Acknowledgments 🙏

- AI video generation services for their amazing APIs
- TikTok automation libraries that inspired this project
- The open-source community for continuous support

---

Made with ❤️ by the TikTok AI Bot Team