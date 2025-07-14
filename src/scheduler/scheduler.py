"""
Post Scheduler for TikTok AI Video Bot
Handles automated posting at optimal times
"""

import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import schedule
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..config import get_settings
from ..logger import setup_logger, log_scheduler_event
from ..database import get_db_ops

logger = setup_logger(__name__)

class PostScheduler:
    """Automated posting scheduler"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_ops = get_db_ops()
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.stats = {
            "posts_scheduled": 0,
            "posts_completed": 0,
            "posts_failed": 0,
            "last_post": None
        }
    
    async def start(self, daemon: bool = False) -> None:
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting post scheduler...")
        
        # Configure scheduled posts
        self._setup_scheduled_posts()
        
        # Start the scheduler
        self.scheduler.start()
        self.is_running = True
        
        log_scheduler_event("scheduler_started", {
            "daemon": daemon,
            "post_times": self.settings.post_times_list,
            "daily_count": self.settings.daily_post_count
        })
        
        if daemon:
            # Run in background
            logger.info("Scheduler running in daemon mode")
            try:
                while self.is_running:
                    await asyncio.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                self.stop()
        else:
            # Block until stopped
            try:
                while self.is_running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                self.stop()
    
    def stop(self) -> None:
        """Stop the scheduler"""
        if not self.is_running:
            return
        
        logger.info("Stopping post scheduler...")
        self.scheduler.shutdown()
        self.is_running = False
        
        log_scheduler_event("scheduler_stopped", self.stats)
    
    def _setup_scheduled_posts(self) -> None:
        """Setup scheduled posting jobs"""
        
        for post_time in self.settings.post_times_list:
            try:
                hour, minute = map(int, post_time.split(':'))
                
                # Create cron trigger for daily posting
                trigger = CronTrigger(
                    hour=hour,
                    minute=minute,
                    timezone=self.settings.timezone
                )
                
                # Add job to scheduler
                self.scheduler.add_job(
                    func=self._execute_scheduled_post,
                    trigger=trigger,
                    id=f"daily_post_{post_time}",
                    name=f"Daily TikTok Post at {post_time}",
                    replace_existing=True
                )
                
                logger.info(f"Scheduled daily post at {post_time}")
                
            except ValueError as e:
                logger.error(f"Invalid time format '{post_time}': {e}")
        
        # Add queue maintenance job (every 2 hours)
        self.scheduler.add_job(
            func=self._maintain_queue,
            trigger="interval",
            hours=2,
            id="queue_maintenance",
            name="Queue Maintenance",
            replace_existing=True
        )
        
        # Add daily reset job (at midnight)
        self.scheduler.add_job(
            func=self._daily_reset,
            trigger=CronTrigger(hour=0, minute=0),
            id="daily_reset",
            name="Daily Reset",
            replace_existing=True
        )
        
        logger.info(f"Configured {len(self.settings.post_times_list)} daily posting times")
    
    async def _execute_scheduled_post(self) -> None:
        """Execute a scheduled post"""
        
        try:
            log_scheduler_event("scheduled_post_started", {
                "time": datetime.now(timezone.utc).isoformat()
            })
            
            # Import here to avoid circular imports
            from ..content.manager import ContentManager
            from ..tiktok.uploader import TikTokUploader
            
            content_manager = ContentManager()
            uploader = TikTokUploader()
            
            # Get next video from queue
            queue_video = content_manager.get_next_video()
            
            if not queue_video:
                logger.warning("No videos in queue for scheduled post")
                await self._handle_empty_queue()
                return
            
            # Check if we can upload
            account_username = self.settings.tiktok_username
            if not account_username:
                logger.error("No TikTok account configured")
                self.stats["posts_failed"] += 1
                return
            
            limits_check = await uploader.check_upload_limits(account_username)
            if not limits_check["can_upload"]:
                logger.warning(f"Cannot upload: {limits_check['reason']}")
                self.stats["posts_failed"] += 1
                return
            
            # Upload the video
            metadata = queue_video.get('metadata', {})
            
            result = await uploader.upload_video(
                video_path=queue_video['video_path'],
                caption=metadata.get('caption', ''),
                hashtags=metadata.get('hashtags', []),
                account_username=account_username
            )
            
            if result['success']:
                self.stats["posts_completed"] += 1
                self.stats["last_post"] = datetime.now(timezone.utc).isoformat()
                
                log_scheduler_event("scheduled_post_success", {
                    "video_path": queue_video['video_path'],
                    "theme": queue_video['theme'],
                    "account": account_username
                })
                
                logger.info(f"Scheduled post completed successfully: {queue_video['video_path']}")
            else:
                self.stats["posts_failed"] += 1
                
                log_scheduler_event("scheduled_post_failed", {
                    "video_path": queue_video['video_path'],
                    "error": result.get('error', 'Unknown error')
                })
                
                logger.error(f"Scheduled post failed: {result.get('error')}")
        
        except Exception as e:
            self.stats["posts_failed"] += 1
            logger.error(f"Scheduled post execution failed: {e}")
            
            log_scheduler_event("scheduled_post_error", {
                "error": str(e)
            })
    
    async def _handle_empty_queue(self) -> None:
        """Handle empty queue by generating new videos"""
        try:
            logger.info("Queue empty, generating new videos...")
            
            # Import here to avoid circular imports
            from ..ai_services.video_generator import AIVideoGenerator
            from ..content.manager import ContentManager
            
            ai_generator = AIVideoGenerator()
            content_manager = ContentManager()
            
            # Generate a few videos quickly
            themes = self.settings.themes_list
            
            for i in range(3):  # Generate 3 videos
                try:
                    import random
                    theme = random.choice(themes)
                    
                    # Generate content prompt
                    content_data = await content_manager.generate_content_prompt(theme)
                    
                    # Generate video
                    video_path = await ai_generator.generate_video(
                        prompt=content_data['prompt'],
                        theme=content_data['theme'],
                        duration=self.settings.default_video_duration
                    )
                    
                    # Add to queue
                    content_manager.add_to_queue(video_path, content_data)
                    
                    logger.info(f"Emergency video generated: {video_path}")
                    
                    # Small delay between generations
                    await asyncio.sleep(10)
                    
                except Exception as e:
                    logger.error(f"Failed to generate emergency video {i+1}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to handle empty queue: {e}")
    
    async def _maintain_queue(self) -> None:
        """Maintain content queue by generating new videos if needed"""
        try:
            from ..content.manager import ContentManager
            content_manager = ContentManager()
            
            # Check current queue size
            queue_status = content_manager.get_queue_status()
            current_size = len(queue_status)
            
            target_size = self.settings.content_queue_size
            
            if current_size < target_size // 2:  # If less than half full
                logger.info(f"Queue maintenance: {current_size}/{target_size} videos, generating more...")
                
                # Generate videos to fill queue
                from ..ai_services.video_generator import AIVideoGenerator
                ai_generator = AIVideoGenerator()
                
                videos_to_generate = min(5, target_size - current_size)  # Max 5 at a time
                
                for i in range(videos_to_generate):
                    try:
                        import random
                        theme = random.choice(self.settings.themes_list)
                        
                        # Generate content
                        content_data = await content_manager.generate_content_prompt(theme)
                        
                        # Generate video
                        video_path = await ai_generator.generate_video(
                            prompt=content_data['prompt'],
                            theme=content_data['theme'],
                            duration=self.settings.default_video_duration
                        )
                        
                        # Add to queue
                        content_manager.add_to_queue(video_path, content_data)
                        
                        logger.info(f"Queue maintenance: Generated {i+1}/{videos_to_generate}")
                        
                        # Delay between generations
                        await asyncio.sleep(30)
                        
                    except Exception as e:
                        logger.error(f"Queue maintenance generation failed: {e}")
                
                log_scheduler_event("queue_maintenance", {
                    "original_size": current_size,
                    "videos_generated": videos_to_generate,
                    "new_size": len(content_manager.get_queue_status())
                })
            
            else:
                logger.info(f"Queue maintenance: {current_size}/{target_size} videos, no action needed")
        
        except Exception as e:
            logger.error(f"Queue maintenance failed: {e}")
    
    async def _daily_reset(self) -> None:
        """Reset daily counters and statistics"""
        try:
            # Reset daily upload counts for all accounts
            accounts = self.db_ops.list_accounts()
            
            for account in accounts:
                # Reset daily upload count (this would need a new DB method)
                # For now, we'll log it
                logger.info(f"Daily reset for account: {account.username}")
            
            # Log daily statistics
            log_scheduler_event("daily_reset", {
                "date": datetime.now(timezone.utc).date().isoformat(),
                "stats": self.stats.copy()
            })
            
            # Reset scheduler stats
            self.stats = {
                "posts_scheduled": 0,
                "posts_completed": 0,
                "posts_failed": 0,
                "last_post": self.stats.get("last_post")  # Keep last post time
            }
            
            logger.info("Daily reset completed")
        
        except Exception as e:
            logger.error(f"Daily reset failed: {e}")
    
    def schedule_custom_post(
        self,
        video_path: str,
        schedule_time: datetime,
        caption: str = "",
        hashtags: List[str] = None,
        account_username: str = None
    ) -> str:
        """Schedule a custom post at specific time"""
        
        job_id = f"custom_post_{int(time.time())}"
        
        self.scheduler.add_job(
            func=self._execute_custom_post,
            trigger="date",
            run_date=schedule_time,
            args=[video_path, caption, hashtags, account_username],
            id=job_id,
            name=f"Custom Post: {video_path}",
            replace_existing=True
        )
        
        self.stats["posts_scheduled"] += 1
        
        log_scheduler_event("custom_post_scheduled", {
            "job_id": job_id,
            "video_path": video_path,
            "schedule_time": schedule_time.isoformat(),
            "account": account_username
        })
        
        logger.info(f"Custom post scheduled for {schedule_time}: {video_path}")
        return job_id
    
    async def _execute_custom_post(
        self,
        video_path: str,
        caption: str,
        hashtags: List[str],
        account_username: str
    ) -> None:
        """Execute a custom scheduled post"""
        
        try:
            from ..tiktok.uploader import TikTokUploader
            uploader = TikTokUploader()
            
            if not account_username:
                account_username = self.settings.tiktok_username
            
            result = await uploader.upload_video(
                video_path=video_path,
                caption=caption,
                hashtags=hashtags or [],
                account_username=account_username
            )
            
            if result['success']:
                self.stats["posts_completed"] += 1
                logger.info(f"Custom scheduled post completed: {video_path}")
            else:
                self.stats["posts_failed"] += 1
                logger.error(f"Custom scheduled post failed: {result.get('error')}")
        
        except Exception as e:
            self.stats["posts_failed"] += 1
            logger.error(f"Custom post execution failed: {e}")
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of scheduled jobs"""
        jobs = []
        
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return jobs
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return {
            "is_running": self.is_running,
            "stats": self.stats.copy(),
            "scheduled_jobs": len(self.scheduler.get_jobs()),
            "next_posts": [
                {
                    "job_id": job.id,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
                if "daily_post" in job.id
            ]
        }