"""
TikTok AI Video Bot - Main Bot Class
Coordinates AI video generation, content management, and TikTok posting
"""

import asyncio
import time
import random
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone, timedelta

from .config import get_settings
from .logger import setup_logger, log_async_performance
from .database import get_db_ops
from .ai_services.video_generator import AIVideoGenerator
from .content.manager import ContentManager
from .tiktok.uploader import TikTokUploader, TikTokAccountManager
from .scheduler.scheduler import PostScheduler

logger = setup_logger(__name__)

class TikTokBot:
    """Main TikTok AI Video Bot"""
    
    def __init__(self):
        self.settings = get_settings()
        self.settings.ensure_directories()
        
        self.db_ops = get_db_ops()
        self.ai_generator = AIVideoGenerator()
        self.content_manager = ContentManager()
        self.uploader = TikTokUploader()
        self.account_manager = TikTokAccountManager()
        self.scheduler = PostScheduler()
        
        logger.info("TikTok AI Video Bot initialized")
    
    @log_async_performance
    async def generate_video(
        self,
        theme: str = None,
        style: str = "cinematic",
        duration: int = None,
        service: str = None
    ) -> str:
        """Generate AI video with content"""
        
        # Use settings defaults if not specified
        if not duration:
            duration = self.settings.default_video_duration
        
        # Generate content prompt
        content_data = await self.content_manager.generate_content_prompt(theme)
        
        logger.info(f"Generating video for theme: {content_data['theme']}")
        
        # Generate video using AI service
        video_path = await self.ai_generator.generate_video(
            prompt=content_data['prompt'],
            theme=content_data['theme'],
            style=style,
            duration=duration,
            service=service
        )
        
        # Add to content queue with metadata
        self.content_manager.add_to_queue(video_path, content_data)
        
        logger.info(f"Video generated and queued: {video_path}")
        return video_path
    
    @log_async_performance
    async def post_video(
        self,
        video_path: str = None,
        caption: str = None,
        hashtags: List[str] = None,
        account_username: str = None,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Post video to TikTok"""
        
        # Get video from queue if not specified
        if not video_path:
            queue_video = self.content_manager.get_next_video()
            if not queue_video:
                raise ValueError("No videos in queue and no video specified")
            
            video_path = queue_video['video_path']
            metadata = queue_video.get('metadata', {})
            
            # Use metadata for caption and hashtags if not provided
            if not caption:
                caption = metadata.get('caption', '')
            if not hashtags:
                hashtags = metadata.get('hashtags', [])
        
        # Validate video file
        validation = self.uploader.validate_video_file(video_path)
        if not validation['valid']:
            raise ValueError(f"Invalid video file: {validation['error']}")
        
        # Check upload limits
        if not account_username:
            account_username = self.settings.tiktok_username
        
        limits_check = await self.uploader.check_upload_limits(account_username)
        if not limits_check['can_upload']:
            raise ValueError(f"Cannot upload: {limits_check['reason']}")
        
        # Upload video
        result = await self.uploader.upload_video(
            video_path=video_path,
            caption=caption,
            hashtags=hashtags,
            account_username=account_username,
            schedule_time=schedule_time
        )
        
        return result
    
    @log_async_performance
    async def generate_and_post(
        self,
        theme: str = None,
        account_username: str = None,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate video and post it immediately"""
        
        try:
            # Generate video
            video_path = await self.generate_video(theme=theme)
            
            # Post video
            result = await self.post_video(
                video_path=video_path,
                account_username=account_username,
                schedule_time=schedule_time
            )
            
            return {
                "success": True,
                "video_path": video_path,
                "upload_result": result
            }
            
        except Exception as e:
            logger.error(f"Generate and post failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def populate_queue(self, count: int = 10, themes: List[str] = None) -> List[str]:
        """Populate content queue with generated videos"""
        
        if not themes:
            themes = self.settings.themes_list
        
        generated_videos = []
        
        for i in range(count):
            try:
                # Select random theme
                theme = random.choice(themes)
                
                # Generate video
                video_path = await self.generate_video(theme=theme)
                generated_videos.append(video_path)
                
                logger.info(f"Generated video {i+1}/{count}: {video_path}")
                
                # Add delay between generations to avoid overwhelming APIs
                if i < count - 1:  # Don't delay after last video
                    delay = random.randint(5, 15)
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to generate video {i+1}: {e}")
        
        logger.info(f"Queue populated with {len(generated_videos)} videos")
        return generated_videos
    
    async def start_scheduler(self, daemon: bool = False) -> None:
        """Start automated posting scheduler"""
        
        logger.info("Starting TikTok posting scheduler")
        
        # Ensure we have videos in queue
        queue_status = self.content_manager.get_queue_status()
        if len(queue_status) < 5:
            logger.info("Queue low, generating more videos...")
            await self.populate_queue(count=10)
        
        # Start scheduler
        await self.scheduler.start(daemon=daemon)
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler"""
        self.scheduler.stop()
        logger.info("Scheduler stopped")
    
    # Account management methods
    def add_account(self, username: str, cookies_file: str = None) -> bool:
        """Add TikTok account"""
        if not cookies_file:
            cookies_file = f"cookies/{username}_cookies.txt"
        
        return self.account_manager.add_account(username, cookies_file)
    
    def list_accounts(self) -> List[Dict[str, Any]]:
        """List all TikTok accounts"""
        return self.account_manager.list_accounts()
    
    def get_account_status(self, username: str) -> Dict[str, Any]:
        """Get account status"""
        return self.account_manager.get_account_status(username)
    
    # Statistics and monitoring
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        db_stats = self.db_ops.get_statistics()
        
        # Add queue information
        queue_status = self.content_manager.get_queue_status()
        db_stats['queue_size'] = len(queue_status)
        
        # Add account information
        accounts = self.list_accounts()
        db_stats['total_accounts'] = len(accounts)
        db_stats['active_accounts'] = len([a for a in accounts if a['status'] == 'active'])
        
        # Calculate success rates
        if db_stats['total_generations'] > 0:
            db_stats['videos_generated'] = db_stats['total_generations']
            db_stats['success_rate'] = (
                db_stats['successful_posts'] / db_stats['total_posts'] * 100 
                if db_stats['total_posts'] > 0 else 0
            )
        
        return db_stats
    
    def get_recent_activity(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent bot activity"""
        recent_generations = self.db_ops.get_video_generations(limit=limit)
        
        activity = {
            "recent_generations": [
                {
                    "id": gen.id,
                    "service": gen.service,
                    "theme": gen.theme,
                    "status": gen.status,
                    "created_at": gen.created_at.isoformat(),
                    "generation_time": gen.generation_time
                }
                for gen in recent_generations
            ]
        }
        
        return activity
    
    # Content management methods
    async def create_content_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """Create content calendar"""
        return self.content_manager.create_content_calendar(days)
    
    def get_queue_status(self) -> List[Dict[str, Any]]:
        """Get content queue status"""
        return self.content_manager.get_queue_status()
    
    # Utility methods
    def clean_cache(self) -> int:
        """Clean temporary files and cache"""
        cleaned_files = 0
        
        # Clean old generated videos (keep last 50)
        videos_dir = Path(self.settings.videos_dir)
        if videos_dir.exists():
            video_files = list(videos_dir.glob("*.mp4"))
            video_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Keep only the 50 most recent files
            files_to_delete = video_files[:-50] if len(video_files) > 50 else []
            
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    cleaned_files += 1
                except Exception as e:
                    logger.warning(f"Could not delete {file_path}: {e}")
        
        # Clean old log files (keep last 30 days)
        logs_dir = Path(self.settings.logs_dir)
        if logs_dir.exists():
            cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 days
            
            for log_file in logs_dir.glob("*.log*"):
                try:
                    if log_file.stat().st_mtime < cutoff_time:
                        log_file.unlink()
                        cleaned_files += 1
                except Exception as e:
                    logger.warning(f"Could not delete log file {log_file}: {e}")
        
        logger.info(f"Cleaned {cleaned_files} temporary files")
        return cleaned_files
    
    def load_config(self, config_file: str) -> None:
        """Load configuration from file"""
        from .config import load_custom_config
        
        new_settings = load_custom_config(config_file)
        self.settings = new_settings
        
        # Reinitialize components with new settings
        self.ai_generator = AIVideoGenerator()
        self.content_manager = ContentManager()
        self.uploader = TikTokUploader()
        self.account_manager = TikTokAccountManager()
        self.scheduler = PostScheduler()
        
        logger.info(f"Configuration loaded from {config_file}")
    
    async def test_services(self) -> Dict[str, Any]:
        """Test all services and connections"""
        results = {}
        
        # Test AI video generation services
        try:
            video_path = await self.ai_generator.test_service("aiml")
            results["ai_generation"] = {"status": "success", "test_video": video_path}
        except Exception as e:
            results["ai_generation"] = {"status": "failed", "error": str(e)}
        
        # Test TikTok upload capabilities
        results["upload_methods"] = {
            "available": self.uploader.available_methods,
            "preferred": self.uploader.preferred_method
        }
        
        # Test database connection
        try:
            stats = self.get_statistics()
            results["database"] = {"status": "success", "stats": stats}
        except Exception as e:
            results["database"] = {"status": "failed", "error": str(e)}
        
        # Test account configuration
        accounts = self.list_accounts()
        results["accounts"] = {
            "total": len(accounts),
            "accounts": accounts
        }
        
        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {}
        }
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.settings.videos_dir)
            free_gb = free // (1024**3)
            
            health["checks"]["disk_space"] = {
                "status": "ok" if free_gb > 5 else "warning",
                "free_gb": free_gb,
                "message": f"{free_gb}GB free" if free_gb > 5 else "Low disk space"
            }
        except Exception as e:
            health["checks"]["disk_space"] = {"status": "error", "error": str(e)}
        
        # Check queue size
        queue_size = len(self.get_queue_status())
        health["checks"]["queue"] = {
            "status": "ok" if queue_size > 5 else "warning",
            "size": queue_size,
            "message": f"{queue_size} videos queued" if queue_size > 5 else "Queue low"
        }
        
        # Check API keys
        api_keys = self.settings.validate_api_keys()
        configured_keys = sum(api_keys.values())
        health["checks"]["api_keys"] = {
            "status": "ok" if configured_keys > 0 else "error",
            "configured": configured_keys,
            "keys": api_keys
        }
        
        # Overall status
        failed_checks = [
            check for check in health["checks"].values() 
            if check["status"] == "error"
        ]
        
        if failed_checks:
            health["status"] = "unhealthy"
        elif any(check["status"] == "warning" for check in health["checks"].values()):
            health["status"] = "degraded"
        
        return health
    
    # Context manager support for cleanup
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Clean up resources
        if hasattr(self.scheduler, 'stop'):
            self.scheduler.stop()
        
        # Close database connections
        if hasattr(self.db_ops, 'close'):
            self.db_ops.db_manager.close()
        
        logger.info("TikTok Bot cleaned up")