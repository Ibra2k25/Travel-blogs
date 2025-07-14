"""
Database models and management for TikTok AI Video Bot
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import get_settings

Base = declarative_base()

# Database Models
class TikTokAccount(Base):
    """TikTok account management"""
    __tablename__ = "tiktok_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    cookies_file = Column(String, nullable=False)
    status = Column(String, default="active")  # active, disabled, banned
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)
    daily_upload_count = Column(Integer, default=0)
    total_uploads = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    metadata = Column(JSON, default=dict)

class VideoGeneration(Base):
    """Video generation tracking"""
    __tablename__ = "video_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, nullable=False)  # runway, pika, kling, etc.
    prompt = Column(Text, nullable=False)
    theme = Column(String, nullable=False)
    style = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)
    aspect_ratio = Column(String, default="9:16")
    status = Column(String, nullable=False)  # pending, success, failed
    video_path = Column(String, nullable=True)
    generation_time = Column(Float, nullable=True)  # seconds
    file_size = Column(Integer, nullable=True)  # bytes
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default=dict)

class TikTokPost(Base):
    """TikTok post tracking"""
    __tablename__ = "tiktok_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_username = Column(String, nullable=False)
    video_generation_id = Column(Integer, nullable=True)
    video_path = Column(String, nullable=False)
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, default=list)
    scheduled_time = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)  # scheduled, posted, failed
    tiktok_video_id = Column(String, nullable=True)
    upload_time = Column(Float, nullable=True)  # seconds
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default=dict)

class ContentQueue(Base):
    """Video content queue"""
    __tablename__ = "content_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    video_generation_id = Column(Integer, nullable=False)
    video_path = Column(String, nullable=False)
    theme = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    scheduled_for = Column(DateTime, nullable=True)
    status = Column(String, default="queued")  # queued, scheduled, posted, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default=dict)

class Analytics(Base):
    """Analytics and performance tracking"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False)
    metric_name = Column(String, nullable=False)  # views, likes, shares, comments
    metric_value = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default=dict)

class SystemLog(Base):
    """System operation logs"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)  # generation, upload, error, etc.
    message = Column(Text, nullable=False)
    level = Column(String, default="INFO")  # DEBUG, INFO, WARNING, ERROR
    service = Column(String, nullable=True)
    execution_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata = Column(JSON, default=dict)

# Database Management
class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = create_engine(self.settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connections"""
        self.engine.dispose()

# Async Database Manager
class AsyncDatabaseManager:
    """Async database operations manager"""
    
    def __init__(self):
        self.settings = get_settings()
        # Convert sqlite URL to async format
        db_url = self.settings.database_url
        if db_url.startswith("sqlite:///"):
            db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        
        self.engine = create_async_engine(db_url)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
    
    async def create_tables(self):
        """Create all database tables asynchronously"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        return self.async_session()
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()

# Database operations
class DatabaseOperations:
    """Database CRUD operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    # Account operations
    def create_account(self, username: str, cookies_file: str) -> TikTokAccount:
        """Create new TikTok account"""
        with self.db_manager.get_session() as db:
            account = TikTokAccount(username=username, cookies_file=cookies_file)
            db.add(account)
            db.commit()
            db.refresh(account)
            return account
    
    def get_account(self, username: str) -> Optional[TikTokAccount]:
        """Get TikTok account by username"""
        with self.db_manager.get_session() as db:
            return db.query(TikTokAccount).filter(TikTokAccount.username == username).first()
    
    def list_accounts(self) -> List[TikTokAccount]:
        """List all TikTok accounts"""
        with self.db_manager.get_session() as db:
            return db.query(TikTokAccount).all()
    
    def update_account_usage(self, username: str):
        """Update account last used time"""
        with self.db_manager.get_session() as db:
            account = db.query(TikTokAccount).filter(TikTokAccount.username == username).first()
            if account:
                account.last_used = datetime.now(timezone.utc)
                account.daily_upload_count += 1
                account.total_uploads += 1
                db.commit()
    
    # Video generation operations
    def create_video_generation(self, **kwargs) -> VideoGeneration:
        """Create video generation record"""
        with self.db_manager.get_session() as db:
            video_gen = VideoGeneration(**kwargs)
            db.add(video_gen)
            db.commit()
            db.refresh(video_gen)
            return video_gen
    
    def update_video_generation(self, id: int, **kwargs):
        """Update video generation record"""
        with self.db_manager.get_session() as db:
            video_gen = db.query(VideoGeneration).filter(VideoGeneration.id == id).first()
            if video_gen:
                for key, value in kwargs.items():
                    setattr(video_gen, key, value)
                db.commit()
    
    def get_video_generations(self, limit: int = 50) -> List[VideoGeneration]:
        """Get recent video generations"""
        with self.db_manager.get_session() as db:
            return db.query(VideoGeneration).order_by(VideoGeneration.created_at.desc()).limit(limit).all()
    
    # Post operations
    def create_post(self, **kwargs) -> TikTokPost:
        """Create TikTok post record"""
        with self.db_manager.get_session() as db:
            post = TikTokPost(**kwargs)
            db.add(post)
            db.commit()
            db.refresh(post)
            return post
    
    def update_post(self, id: int, **kwargs):
        """Update TikTok post record"""
        with self.db_manager.get_session() as db:
            post = db.query(TikTokPost).filter(TikTokPost.id == id).first()
            if post:
                for key, value in kwargs.items():
                    setattr(post, key, value)
                db.commit()
    
    # Queue operations
    def add_to_queue(self, video_generation_id: int, video_path: str, theme: str, **kwargs) -> ContentQueue:
        """Add video to content queue"""
        with self.db_manager.get_session() as db:
            queue_item = ContentQueue(
                video_generation_id=video_generation_id,
                video_path=video_path,
                theme=theme,
                **kwargs
            )
            db.add(queue_item)
            db.commit()
            db.refresh(queue_item)
            return queue_item
    
    def get_queue(self, limit: int = 20) -> List[ContentQueue]:
        """Get content queue"""
        with self.db_manager.get_session() as db:
            return db.query(ContentQueue).filter(
                ContentQueue.status == "queued"
            ).order_by(ContentQueue.priority.desc(), ContentQueue.created_at.asc()).limit(limit).all()
    
    def get_next_queued_video(self) -> Optional[ContentQueue]:
        """Get next video from queue"""
        with self.db_manager.get_session() as db:
            return db.query(ContentQueue).filter(
                ContentQueue.status == "queued"
            ).order_by(ContentQueue.priority.desc(), ContentQueue.created_at.asc()).first()
    
    # Analytics operations
    def log_event(self, event_type: str, message: str, **kwargs):
        """Log system event"""
        with self.db_manager.get_session() as db:
            log = SystemLog(
                event_type=event_type,
                message=message,
                **kwargs
            )
            db.add(log)
            db.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        with self.db_manager.get_session() as db:
            total_generations = db.query(VideoGeneration).count()
            successful_generations = db.query(VideoGeneration).filter(VideoGeneration.status == "success").count()
            total_posts = db.query(TikTokPost).count()
            successful_posts = db.query(TikTokPost).filter(TikTokPost.status == "posted").count()
            queue_size = db.query(ContentQueue).filter(ContentQueue.status == "queued").count()
            active_accounts = db.query(TikTokAccount).filter(TikTokAccount.status == "active").count()
            
            generation_success_rate = (successful_generations / total_generations * 100) if total_generations > 0 else 0
            post_success_rate = (successful_posts / total_posts * 100) if total_posts > 0 else 0
            
            return {
                "total_generations": total_generations,
                "successful_generations": successful_generations,
                "generation_success_rate": generation_success_rate,
                "total_posts": total_posts,
                "successful_posts": successful_posts,
                "post_success_rate": post_success_rate,
                "queue_size": queue_size,
                "active_accounts": active_accounts
            }

# Global database instances
db_manager = None
db_ops = None

def init_database():
    """Initialize database"""
    global db_manager, db_ops
    
    settings = get_settings()
    settings.ensure_directories()
    
    db_manager = DatabaseManager()
    db_manager.create_tables()
    db_ops = DatabaseOperations(db_manager)
    
    return db_manager, db_ops

def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    global db_manager
    if db_manager is None:
        init_database()
    return db_manager

def get_db_ops() -> DatabaseOperations:
    """Get database operations instance"""
    global db_ops
    if db_ops is None:
        init_database()
    return db_ops