"""
TikTok Upload Automation Service
Handles video uploading to TikTok using multiple automation libraries
"""

import asyncio
import time
import random
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
from datetime import datetime, timezone, timedelta

try:
    from tiktokautouploader import upload_tiktok
    TIKTOK_AUTO_UPLOADER_AVAILABLE = True
except ImportError:
    TIKTOK_AUTO_UPLOADER_AVAILABLE = False

try:
    from tiktok_uploader.upload import upload_video as tiktok_uploader_upload
    from tiktok_uploader.auth import AuthBackend
    TIKTOK_UPLOADER_AVAILABLE = True
except ImportError:
    TIKTOK_UPLOADER_AVAILABLE = False

from ..config import get_settings
from ..logger import setup_logger, log_async_performance, log_tiktok_upload
from ..database import get_db_ops

logger = setup_logger(__name__)

class TikTokUploader:
    """TikTok video upload automation"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_ops = get_db_ops()
        self.available_methods = self._check_available_methods()
        self.preferred_method = self._select_preferred_method()
    
    def _check_available_methods(self) -> List[str]:
        """Check which upload methods are available"""
        methods = []
        
        if TIKTOK_AUTO_UPLOADER_AVAILABLE:
            methods.append("tiktokautouploader")
        
        if TIKTOK_UPLOADER_AVAILABLE:
            methods.append("tiktok_uploader")
        
        # Always have manual method as fallback
        methods.append("manual")
        
        logger.info(f"Available upload methods: {methods}")
        return methods
    
    def _select_preferred_method(self) -> str:
        """Select preferred upload method"""
        # Prefer tiktokautouploader for its advanced features
        if "tiktokautouploader" in self.available_methods:
            return "tiktokautouploader"
        elif "tiktok_uploader" in self.available_methods:
            return "tiktok_uploader"
        else:
            return "manual"
    
    @log_async_performance
    async def upload_video(
        self,
        video_path: str,
        caption: str = "",
        hashtags: List[str] = None,
        account_username: str = None,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Upload video to TikTok"""
        
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Get account info
        if not account_username:
            account_username = self.settings.tiktok_username
        
        if not account_username:
            raise ValueError("No TikTok account configured")
        
        # Create post record
        post_record = self.db_ops.create_post(
            account_username=account_username,
            video_path=video_path,
            caption=caption,
            hashtags=hashtags or [],
            scheduled_time=schedule_time,
            status="uploading"
        )
        
        start_time = time.time()
        
        try:
            # Format caption with hashtags
            full_caption = self._format_caption(caption, hashtags)
            
            # Upload using preferred method
            result = await self._upload_with_method(
                self.preferred_method,
                video_path,
                full_caption,
                account_username,
                schedule_time
            )
            
            upload_time = time.time() - start_time
            
            # Update post record
            self.db_ops.update_post(
                post_record.id,
                status="posted" if result["success"] else "failed",
                posted_at=datetime.now(timezone.utc) if result["success"] else None,
                tiktok_video_id=result.get("video_id"),
                upload_time=upload_time,
                error_message=result.get("error")
            )
            
            # Update account usage
            if result["success"]:
                self.db_ops.update_account_usage(account_username)
            
            # Log the upload
            log_tiktok_upload(
                username=account_username,
                video_path=video_path,
                status="success" if result["success"] else "failed",
                execution_time=upload_time,
                error=result.get("error")
            )
            
            return result
            
        except Exception as e:
            upload_time = time.time() - start_time
            error_message = str(e)
            
            # Update post record
            self.db_ops.update_post(
                post_record.id,
                status="failed",
                error_message=error_message,
                upload_time=upload_time
            )
            
            # Log the failed upload
            log_tiktok_upload(
                username=account_username,
                video_path=video_path,
                status="failed",
                execution_time=upload_time,
                error=error_message
            )
            
            logger.error(f"TikTok upload failed: {e}")
            raise
    
    async def _upload_with_method(
        self,
        method: str,
        video_path: str,
        caption: str,
        account_username: str,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Upload video using specific method"""
        
        if method == "tiktokautouploader":
            return await self._upload_with_tiktokautouploader(
                video_path, caption, account_username, schedule_time
            )
        elif method == "tiktok_uploader":
            return await self._upload_with_tiktok_uploader(
                video_path, caption, account_username, schedule_time
            )
        elif method == "manual":
            return await self._upload_manual(
                video_path, caption, account_username, schedule_time
            )
        else:
            raise ValueError(f"Unknown upload method: {method}")
    
    async def _upload_with_tiktokautouploader(
        self,
        video_path: str,
        caption: str,
        account_username: str,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Upload using tiktokautouploader library"""
        
        if not TIKTOK_AUTO_UPLOADER_AVAILABLE:
            raise ImportError("tiktokautouploader not available")
        
        try:
            # Prepare upload parameters
            upload_params = {
                "video": video_path,
                "description": caption,
                "accountname": account_username,
                "hashtags": self._extract_hashtags_from_caption(caption),
                "copyrightcheck": True,  # Enable copyright checking
                "sound_name": None,  # Could add trending sound selection
                "sound_aud_vol": "main"
            }
            
            # Add scheduling if specified
            if schedule_time:
                # Convert to the format expected by tiktokautouploader
                schedule_params = self._format_schedule_time(schedule_time)
                upload_params.update(schedule_params)
            
            # Add human-like behavior delays
            if self.settings.enable_humanlike_behavior:
                delay = random.randint(
                    self.settings.upload_delay_min,
                    self.settings.upload_delay_max
                )
                logger.info(f"Waiting {delay} seconds for human-like behavior")
                await asyncio.sleep(delay)
            
            # Perform upload
            logger.info(f"Uploading video with tiktokautouploader: {video_path}")
            
            # Run in thread pool since it's blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: upload_tiktok(**upload_params)
            )
            
            return {
                "success": True,
                "method": "tiktokautouploader",
                "video_id": None,  # tiktokautouploader doesn't return video ID
                "message": "Upload completed successfully"
            }
            
        except Exception as e:
            logger.error(f"tiktokautouploader upload failed: {e}")
            return {
                "success": False,
                "method": "tiktokautouploader",
                "error": str(e)
            }
    
    async def _upload_with_tiktok_uploader(
        self,
        video_path: str,
        caption: str,
        account_username: str,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Upload using tiktok_uploader library"""
        
        if not TIKTOK_UPLOADER_AVAILABLE:
            raise ImportError("tiktok_uploader not available")
        
        try:
            # Get cookies file for account
            cookies_file = Path(self.settings.tiktok_cookies_file)
            if not cookies_file.exists():
                raise FileNotFoundError(f"Cookies file not found: {cookies_file}")
            
            # Prepare upload parameters
            upload_params = {
                "video": video_path,
                "description": caption,
                "cookies": str(cookies_file),
                "headless": True,  # Run in headless mode
                "browser": "chrome"
            }
            
            # Add scheduling if specified
            if schedule_time:
                upload_params["schedule"] = schedule_time
            
            # Add human-like behavior delays
            if self.settings.enable_humanlike_behavior:
                delay = random.randint(
                    self.settings.upload_delay_min,
                    self.settings.upload_delay_max
                )
                await asyncio.sleep(delay)
            
            # Perform upload
            logger.info(f"Uploading video with tiktok_uploader: {video_path}")
            
            # Run in thread pool since it's blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: tiktok_uploader_upload(**upload_params)
            )
            
            return {
                "success": True,
                "method": "tiktok_uploader",
                "video_id": None,
                "message": "Upload completed successfully"
            }
            
        except Exception as e:
            logger.error(f"tiktok_uploader upload failed: {e}")
            return {
                "success": False,
                "method": "tiktok_uploader",
                "error": str(e)
            }
    
    async def _upload_manual(
        self,
        video_path: str,
        caption: str,
        account_username: str,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Manual upload instructions (fallback method)"""
        
        logger.warning("Using manual upload method - automated upload libraries not available")
        
        # Copy video to a designated folder for manual upload
        manual_upload_dir = Path(self.settings.data_dir) / "manual_uploads"
        manual_upload_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        manual_video_path = manual_upload_dir / f"manual_{timestamp}_{Path(video_path).name}"
        
        # Copy the video file
        import shutil
        shutil.copy2(video_path, manual_video_path)
        
        # Create instruction file
        instruction_file = manual_upload_dir / f"instructions_{timestamp}.txt"
        with open(instruction_file, 'w') as f:
            f.write(f"Manual TikTok Upload Instructions\n")
            f.write(f"====================================\n\n")
            f.write(f"Video File: {manual_video_path}\n")
            f.write(f"Account: {account_username}\n")
            f.write(f"Caption: {caption}\n")
            if schedule_time:
                f.write(f"Schedule Time: {schedule_time}\n")
            f.write(f"\nPlease upload this video manually to TikTok and mark as completed.\n")
        
        logger.info(f"Manual upload files created in: {manual_upload_dir}")
        
        return {
            "success": True,  # Consider it successful since files are prepared
            "method": "manual",
            "manual_upload_path": str(manual_video_path),
            "instructions_file": str(instruction_file),
            "message": "Manual upload files prepared. Please upload manually."
        }
    
    def _format_caption(self, caption: str, hashtags: List[str] = None) -> str:
        """Format caption with hashtags"""
        if not hashtags:
            return caption
        
        # Remove any existing hashtags from caption
        caption_clean = caption
        for hashtag in hashtags:
            caption_clean = caption_clean.replace(hashtag, "").strip()
        
        # Add hashtags to end
        hashtag_str = " ".join(hashtags)
        return f"{caption_clean}\n\n{hashtag_str}".strip()
    
    def _extract_hashtags_from_caption(self, caption: str) -> List[str]:
        """Extract hashtags from caption"""
        import re
        hashtags = re.findall(r'#\w+', caption)
        return hashtags
    
    def _format_schedule_time(self, schedule_time: datetime) -> Dict[str, Any]:
        """Format schedule time for tiktokautouploader"""
        # tiktokautouploader expects time in HH:MM format and day number
        time_str = schedule_time.strftime("%H:%M")
        day = schedule_time.day
        
        return {
            "schedule": time_str,
            "day": day
        }
    
    async def check_upload_limits(self, account_username: str) -> Dict[str, Any]:
        """Check upload limits for account"""
        account = self.db_ops.get_account(account_username)
        
        if not account:
            return {"can_upload": False, "reason": "Account not found"}
        
        # Check daily upload limit
        if account.daily_upload_count >= self.settings.max_daily_uploads:
            return {
                "can_upload": False,
                "reason": f"Daily upload limit reached ({self.settings.max_daily_uploads})"
            }
        
        # Check account status
        if account.status != "active":
            return {
                "can_upload": False,
                "reason": f"Account status: {account.status}"
            }
        
        return {
            "can_upload": True,
            "remaining_uploads": self.settings.max_daily_uploads - account.daily_upload_count
        }
    
    async def get_upload_statistics(self, account_username: str = None) -> Dict[str, Any]:
        """Get upload statistics"""
        stats = self.db_ops.get_statistics()
        
        if account_username:
            account = self.db_ops.get_account(account_username)
            if account:
                stats["account"] = {
                    "username": account.username,
                    "total_uploads": account.total_uploads,
                    "daily_uploads": account.daily_upload_count,
                    "success_rate": account.success_rate,
                    "last_used": account.last_used.isoformat() if account.last_used else None
                }
        
        return stats
    
    def validate_video_file(self, video_path: str) -> Dict[str, Any]:
        """Validate video file for TikTok upload"""
        path = Path(video_path)
        
        if not path.exists():
            return {"valid": False, "error": "File does not exist"}
        
        # Check file size (TikTok limit is ~500MB)
        file_size = path.stat().st_size
        max_size = 500 * 1024 * 1024  # 500MB
        
        if file_size > max_size:
            return {"valid": False, "error": f"File too large: {file_size / 1024 / 1024:.1f}MB (max 500MB)"}
        
        # Check file extension
        allowed_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        if path.suffix.lower() not in allowed_extensions:
            return {"valid": False, "error": f"Invalid file type: {path.suffix}"}
        
        # Check video duration using ffprobe (if available)
        try:
            duration = self._get_video_duration(video_path)
            if duration > 600:  # 10 minutes max
                return {"valid": False, "error": f"Video too long: {duration}s (max 600s)"}
        except Exception as e:
            logger.warning(f"Could not check video duration: {e}")
        
        return {"valid": True, "file_size": file_size}
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', video_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                raise ValueError("ffprobe failed")
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError) as e:
            raise ValueError(f"Could not determine video duration: {e}")

# Account management functions
class TikTokAccountManager:
    """Manages TikTok accounts and authentication"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_ops = get_db_ops()
    
    def add_account(self, username: str, cookies_file: str) -> bool:
        """Add new TikTok account"""
        try:
            # Validate cookies file exists
            if not Path(cookies_file).exists():
                raise FileNotFoundError(f"Cookies file not found: {cookies_file}")
            
            # Create account record
            account = self.db_ops.create_account(username, cookies_file)
            logger.info(f"Added TikTok account: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add account {username}: {e}")
            return False
    
    def list_accounts(self) -> List[Dict[str, Any]]:
        """List all TikTok accounts"""
        accounts = self.db_ops.list_accounts()
        
        return [
            {
                "username": account.username,
                "status": account.status,
                "last_used": account.last_used.strftime("%Y-%m-%d %H:%M:%S") if account.last_used else "Never",
                "total_uploads": account.total_uploads,
                "daily_uploads": account.daily_upload_count
            }
            for account in accounts
        ]
    
    def get_account_status(self, username: str) -> Dict[str, Any]:
        """Get account status and statistics"""
        account = self.db_ops.get_account(username)
        
        if not account:
            return {"exists": False}
        
        return {
            "exists": True,
            "username": account.username,
            "status": account.status,
            "created_at": account.created_at.isoformat(),
            "last_used": account.last_used.isoformat() if account.last_used else None,
            "total_uploads": account.total_uploads,
            "daily_uploads": account.daily_upload_count,
            "success_rate": account.success_rate
        }