"""
Configuration management for TikTok AI Video Bot
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # AI Service APIs
    aiml_api_key: str = Field(default="", env="AIML_API_KEY")
    runway_api_key: str = Field(default="", env="RUNWAY_API_KEY")
    pika_api_key: str = Field(default="", env="PIKA_API_KEY")
    kling_api_key: str = Field(default="", env="KLING_API_KEY")
    minimax_api_key: str = Field(default="", env="MINIMAX_API_KEY")
    luma_api_key: str = Field(default="", env="LUMA_API_KEY")
    google_veo_api_key: str = Field(default="", env="GOOGLE_VEO_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    
    # Content Generation Settings
    default_video_duration: int = Field(default=10, env="DEFAULT_VIDEO_DURATION")
    aspect_ratio: str = Field(default="9:16", env="ASPECT_RATIO")
    video_quality: str = Field(default="1080p", env="VIDEO_QUALITY")
    daily_post_count: int = Field(default=3, env="DAILY_POST_COUNT")
    content_queue_size: int = Field(default=20, env="CONTENT_QUEUE_SIZE")
    
    # Posting Schedule
    optimal_post_times: str = Field(default="09:00,15:00,21:00", env="OPTIMAL_POST_TIMES")
    timezone: str = Field(default="UTC", env="TIMEZONE")
    
    # TikTok Account Settings
    tiktok_username: str = Field(default="", env="TIKTOK_USERNAME")
    tiktok_cookies_file: str = Field(default="cookies/tiktok_cookies.txt", env="TIKTOK_COOKIES_FILE")
    
    # Storage Paths
    videos_dir: str = Field(default="./generated_videos", env="VIDEOS_DIR")
    queue_dir: str = Field(default="./video_queue", env="QUEUE_DIR")
    logs_dir: str = Field(default="./logs", env="LOGS_DIR")
    config_dir: str = Field(default="./config", env="CONFIG_DIR")
    data_dir: str = Field(default="./data", env="DATA_DIR")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./tiktok_bot.db", env="DATABASE_URL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Content Generation
    enable_ai_captions: bool = Field(default=True, env="ENABLE_AI_CAPTIONS")
    enable_hashtag_research: bool = Field(default=True, env="ENABLE_HASHTAG_RESEARCH")
    enable_trending_analysis: bool = Field(default=True, env="ENABLE_TRENDING_ANALYSIS")
    max_hashtags: int = Field(default=10, env="MAX_HASHTAGS")
    
    # Safety and Rate Limiting
    max_daily_uploads: int = Field(default=5, env="MAX_DAILY_UPLOADS")
    upload_delay_min: int = Field(default=30, env="UPLOAD_DELAY_MIN")
    upload_delay_max: int = Field(default=180, env="UPLOAD_DELAY_MAX")
    enable_humanlike_behavior: bool = Field(default=True, env="ENABLE_HUMANLIKE_BEHAVIOR")
    
    # Analytics and Monitoring
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    analytics_db_url: str = Field(default="sqlite:///./analytics.db", env="ANALYTICS_DB_URL")
    track_engagement: bool = Field(default=True, env="TRACK_ENGAGEMENT")
    track_performance: bool = Field(default=True, env="TRACK_PERFORMANCE")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/tiktok_bot.log", env="LOG_FILE")
    enable_file_logging: bool = Field(default=True, env="ENABLE_FILE_LOGGING")
    enable_console_logging: bool = Field(default=True, env="ENABLE_CONSOLE_LOGGING")
    
    # Error Handling
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: int = Field(default=30, env="RETRY_DELAY")
    enable_notifications: bool = Field(default=False, env="ENABLE_NOTIFICATIONS")
    webhook_url: str = Field(default="", env="WEBHOOK_URL")
    
    # Development Settings
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    test_mode: bool = Field(default=False, env="TEST_MODE")
    dry_run: bool = Field(default=False, env="DRY_RUN")
    
    # Proxy Settings
    use_proxy: bool = Field(default=False, env="USE_PROXY")
    proxy_url: str = Field(default="", env="PROXY_URL")
    proxy_rotation: bool = Field(default=False, env="PROXY_ROTATION")
    
    # Content Themes
    default_theme: str = Field(default="motivational", env="DEFAULT_THEME")
    available_themes: str = Field(default="motivational,educational,trending,abstract,nature,urban", env="AVAILABLE_THEMES")
    
    # Video Processing
    ffmpeg_path: str = Field(default="ffmpeg", env="FFMPEG_PATH")
    enable_gpu_acceleration: bool = Field(default=False, env="ENABLE_GPU_ACCELERATION")
    video_codec: str = Field(default="h264", env="VIDEO_CODEC")
    audio_codec: str = Field(default="aac", env="AUDIO_CODEC")
    
    # Social Media Integration
    enable_cross_posting: bool = Field(default=False, env="ENABLE_CROSS_POSTING")
    instagram_username: str = Field(default="", env="INSTAGRAM_USERNAME")
    youtube_shorts_channel: str = Field(default="", env="YOUTUBE_SHORTS_CHANNEL")
    
    # Captcha Solving
    captcha_solver_api_key: str = Field(default="", env="CAPTCHA_SOLVER_API_KEY")
    captcha_solver_service: str = Field(default="2captcha", env="CAPTCHA_SOLVER_SERVICE")
    
    # Monitoring and Alerts
    enable_health_checks: bool = Field(default=True, env="ENABLE_HEALTH_CHECKS")
    health_check_interval: int = Field(default=3600, env="HEALTH_CHECK_INTERVAL")
    alert_email: str = Field(default="", env="ALERT_EMAIL")
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def post_times_list(self) -> List[str]:
        """Convert optimal post times string to list"""
        return [time.strip() for time in self.optimal_post_times.split(',')]
    
    @property
    def themes_list(self) -> List[str]:
        """Convert available themes string to list"""
        return [theme.strip() for theme in self.available_themes.split(',')]
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        directories = [
            self.videos_dir,
            self.queue_dir,
            self.logs_dir,
            self.config_dir,
            self.data_dir,
            "cookies"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate which API keys are configured"""
        keys = {
            "aiml": bool(self.aiml_api_key),
            "runway": bool(self.runway_api_key),
            "pika": bool(self.pika_api_key),
            "kling": bool(self.kling_api_key),
            "minimax": bool(self.minimax_api_key),
            "luma": bool(self.luma_api_key),
            "google_veo": bool(self.google_veo_api_key),
            "openai": bool(self.openai_api_key)
        }
        return keys
    
    def get_ai_service_config(self, service: str) -> Dict[str, Any]:
        """Get configuration for specific AI service"""
        configs = {
            "runway": {
                "api_key": self.runway_api_key,
                "base_url": "https://api.runwayml.com/v1",
                "model": "gen3a_turbo"
            },
            "pika": {
                "api_key": self.pika_api_key,
                "base_url": "https://api.pika.art/v1",
                "model": "pika-2.2"
            },
            "kling": {
                "api_key": self.kling_api_key,
                "base_url": "https://api.kling.kuaishou.com/v1",
                "model": "kling-v1"
            },
            "minimax": {
                "api_key": self.minimax_api_key,
                "base_url": "https://api.minimax.chat/v1",
                "model": "hailuo-02"
            },
            "luma": {
                "api_key": self.luma_api_key,
                "base_url": "https://api.lumalabs.ai/v1",
                "model": "dream-machine"
            },
            "aiml": {
                "api_key": self.aiml_api_key,
                "base_url": "https://api.aimlapi.com/v1",
                "models": {
                    "runway": "gen4_turbo",
                    "pika": "pika-2.2",
                    "kling": "kling-v1.6-pro",
                    "minimax": "hailuo-02",
                    "luma": "luma-ray-1.6"
                }
            }
        }
        return configs.get(service, {})

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings

def load_custom_config(config_path: str) -> Settings:
    """Load settings from custom configuration file"""
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Load additional environment variables from custom file
    load_dotenv(config_path)
    return Settings()

def save_config_template(output_path: str = "config/config_template.env") -> None:
    """Save a configuration template file"""
    template = """# TikTok AI Video Bot Configuration Template
# Copy this to .env and fill in your values

# AI Video Generation Service APIs
AIML_API_KEY=your_aiml_api_key_here
RUNWAY_API_KEY=your_runway_api_key
PIKA_API_KEY=your_pika_api_key
KLING_API_KEY=your_kling_api_key
MINIMAX_API_KEY=your_minimax_api_key
LUMA_API_KEY=your_luma_api_key
OPENAI_API_KEY=your_openai_api_key

# Content Settings
DEFAULT_VIDEO_DURATION=10
DAILY_POST_COUNT=3
OPTIMAL_POST_TIMES=09:00,15:00,21:00

# TikTok Account
TIKTOK_USERNAME=your_tiktok_username
TIKTOK_COOKIES_FILE=cookies/tiktok_cookies.txt

# Storage
VIDEOS_DIR=./generated_videos
LOGS_DIR=./logs

# Safety
MAX_DAILY_UPLOADS=5
ENABLE_HUMANLIKE_BEHAVIOR=true

# Other settings...
"""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(template)