"""
Content Management System
Handles content themes, prompt generation, and queue management
"""

import random
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
import openai
from ..config import get_settings
from ..logger import setup_logger
from ..database import get_db_ops

logger = setup_logger(__name__)

class ContentManager:
    """Manages content creation, themes, and queue"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_ops = get_db_ops()
        self.themes = self._load_themes()
        self.openai_client = None
        
        # Initialize OpenAI if available
        if self.settings.openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
    
    def _load_themes(self) -> Dict[str, Any]:
        """Load content themes configuration"""
        themes_file = Path(self.settings.config_dir) / "themes.json"
        
        if themes_file.exists():
            with open(themes_file, 'r') as f:
                return json.load(f)
        else:
            # Default themes
            return self._get_default_themes()
    
    def _get_default_themes(self) -> Dict[str, Any]:
        """Get default content themes"""
        return {
            "motivational": {
                "description": "Inspirational and motivational content",
                "prompts": [
                    "A person climbing a mountain at sunrise, reaching for their goals",
                    "Lightning striking with powerful energy, representing breakthrough moments",
                    "A seed growing into a mighty tree, symbolizing growth and persistence",
                    "Ocean waves crashing against rocks, showing resilience and power",
                    "A phoenix rising from ashes, representing transformation and renewal"
                ],
                "hashtags": ["#motivation", "#inspiration", "#success", "#mindset", "#goals", "#hustle", "#grind", "#believe"],
                "captions": [
                    "Your only limit is your mind 💪",
                    "Great things never come from comfort zones",
                    "The comeback is always stronger than the setback",
                    "Success starts with self-discipline",
                    "Dream big, work hard, stay focused"
                ]
            },
            "educational": {
                "description": "Educational and informative content",
                "prompts": [
                    "Brain neurons firing, representing learning and knowledge",
                    "Books floating in space, symbolizing infinite knowledge",
                    "DNA double helix rotating, showing scientific discovery",
                    "Mathematical equations forming in golden light",
                    "Historical timeline flowing like a river of knowledge"
                ],
                "hashtags": ["#education", "#learning", "#knowledge", "#facts", "#science", "#history", "#study", "#brain"],
                "captions": [
                    "Knowledge is power 🧠",
                    "Learn something new every day",
                    "Education is the most powerful weapon",
                    "The more you know, the more you grow",
                    "Curiosity is the engine of achievement"
                ]
            },
            "trending": {
                "description": "Current trends and viral content",
                "prompts": [
                    "Neon lights in a futuristic city, trendy and modern",
                    "Social media icons floating in digital space",
                    "Viral content spreading like wildfire across screens",
                    "Trending hashtags materializing in the air",
                    "Modern lifestyle scenes with vibrant colors"
                ],
                "hashtags": ["#trending", "#viral", "#fyp", "#foryou", "#popular", "#trend", "#hot", "#new"],
                "captions": [
                    "This is trending right now! 🔥",
                    "Everyone's talking about this",
                    "The latest trend you need to know",
                    "Going viral for all the right reasons",
                    "Catch this trend before it's gone"
                ]
            },
            "abstract": {
                "description": "Abstract and artistic content",
                "prompts": [
                    "Flowing liquid metal in abstract shapes",
                    "Geometric patterns morphing into organic forms",
                    "Colors bleeding and mixing like watercolors",
                    "Fractal patterns expanding infinitely",
                    "Abstract sculptures forming from light and shadow"
                ],
                "hashtags": ["#abstract", "#art", "#creative", "#artistic", "#design", "#visual", "#aesthetic", "#modern"],
                "captions": [
                    "Art speaks where words are unable to explain",
                    "Abstract beauty in motion",
                    "Creating something from nothing",
                    "Art is the language of the soul",
                    "Beauty lies in the eye of the beholder"
                ]
            },
            "nature": {
                "description": "Natural and serene content",
                "prompts": [
                    "Serene forest with sunlight filtering through trees",
                    "Ocean waves gently lapping against pristine shore",
                    "Mountain peaks covered in snow under starry sky",
                    "Wildflowers swaying in a gentle breeze",
                    "Waterfall cascading into a crystal clear pool"
                ],
                "hashtags": ["#nature", "#peaceful", "#serene", "#natural", "#earth", "#green", "#wildlife", "#zen"],
                "captions": [
                    "Nature is the ultimate artist 🌿",
                    "Find peace in nature's embrace",
                    "Earth's natural beauty never fails to amaze",
                    "Disconnect to reconnect with nature",
                    "Nature doesn't hurry, yet everything is accomplished"
                ]
            },
            "urban": {
                "description": "Urban and city lifestyle content",
                "prompts": [
                    "Bustling city street with neon reflections",
                    "Skyscrapers reaching toward the clouds",
                    "Urban street art coming to life",
                    "City lights creating patterns in the night",
                    "Modern architecture with sleek design"
                ],
                "hashtags": ["#urban", "#city", "#modern", "#lifestyle", "#architecture", "#street", "#downtown", "#metropolitan"],
                "captions": [
                    "City life, bright lights ✨",
                    "Urban jungle vibes",
                    "Where dreams meet concrete",
                    "City that never sleeps",
                    "Modern living at its finest"
                ]
            }
        }
    
    async def generate_content_prompt(self, theme: str = None) -> Dict[str, str]:
        """Generate content prompt for video creation"""
        if not theme:
            theme = random.choice(self.settings.themes_list)
        
        if theme not in self.themes:
            theme = self.settings.default_theme
        
        theme_data = self.themes[theme]
        
        # Use AI to generate creative prompt if OpenAI is available
        if self.openai_client:
            prompt = await self._generate_ai_prompt(theme, theme_data)
        else:
            # Use predefined prompts
            prompt = random.choice(theme_data["prompts"])
        
        # Generate caption
        caption = await self._generate_caption(theme, theme_data)
        
        # Select hashtags
        hashtags = self._select_hashtags(theme_data["hashtags"])
        
        return {
            "theme": theme,
            "prompt": prompt,
            "caption": caption,
            "hashtags": hashtags
        }
    
    async def _generate_ai_prompt(self, theme: str, theme_data: Dict) -> str:
        """Generate creative prompt using OpenAI"""
        try:
            system_prompt = f"""You are a creative AI video prompt generator. Create engaging, visual prompts for {theme} themed videos that will be generated using AI video services like Runway or Pika.

Theme: {theme}
Description: {theme_data['description']}

Requirements:
- Create visually stunning and engaging prompts
- Focus on movement and visual interest
- Keep prompts under 200 characters
- Make them suitable for vertical (9:16) video format
- Ensure they're appropriate for TikTok audience
- Include cinematic and dynamic elements

Example prompts for this theme:
{', '.join(theme_data['prompts'][:3])}

Generate a new, unique prompt that's different from the examples but fits the theme."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate a creative video prompt for {theme} theme"}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"Failed to generate AI prompt: {e}")
            # Fallback to predefined prompts
            return random.choice(theme_data["prompts"])
    
    async def _generate_caption(self, theme: str, theme_data: Dict) -> str:
        """Generate caption for the video"""
        if self.openai_client:
            try:
                system_prompt = f"""Generate a short, engaging TikTok caption for a {theme} themed video. 

Requirements:
- Keep it under 100 characters
- Make it engaging and relatable
- Include relevant emojis
- Use trending language
- Encourage engagement (likes, shares, comments)

Examples for this theme:
{', '.join(theme_data['captions'][:3])}

Generate a new, unique caption."""

                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Generate a TikTok caption for {theme} content"}
                    ],
                    max_tokens=50,
                    temperature=0.9
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.warning(f"Failed to generate AI caption: {e}")
        
        # Fallback to predefined captions
        return random.choice(theme_data["captions"])
    
    def _select_hashtags(self, theme_hashtags: List[str]) -> List[str]:
        """Select hashtags for the post"""
        # Always include some theme-specific hashtags
        selected = random.sample(theme_hashtags, min(4, len(theme_hashtags)))
        
        # Add some general trending hashtags
        general_hashtags = ["#fyp", "#foryou", "#viral", "#trending", "#explore"]
        selected.extend(random.sample(general_hashtags, 2))
        
        # Limit to max hashtags setting
        return selected[:self.settings.max_hashtags]
    
    def add_to_queue(self, video_path: str, content_data: Dict[str, Any] = None) -> None:
        """Add video to content queue"""
        if not content_data:
            content_data = {}
        
        # Get video generation ID from database
        video_generations = self.db_ops.get_video_generations(limit=1)
        video_gen_id = video_generations[0].id if video_generations else 0
        
        self.db_ops.add_to_queue(
            video_generation_id=video_gen_id,
            video_path=video_path,
            theme=content_data.get("theme", "unknown"),
            metadata=content_data
        )
        
        logger.info(f"Added video to queue: {video_path}")
    
    def get_next_video(self) -> Optional[Dict[str, Any]]:
        """Get next video from queue"""
        queue_item = self.db_ops.get_next_queued_video()
        
        if not queue_item:
            return None
        
        return {
            "id": queue_item.id,
            "video_path": queue_item.video_path,
            "theme": queue_item.theme,
            "metadata": queue_item.metadata or {}
        }
    
    def get_queue_status(self) -> List[Dict[str, Any]]:
        """Get current queue status"""
        queue_items = self.db_ops.get_queue(limit=50)
        
        return [
            {
                "id": item.id,
                "video_path": item.video_path,
                "theme": item.theme,
                "created": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": item.status
            }
            for item in queue_items
        ]
    
    def setup_themes_interactive(self) -> List[str]:
        """Interactive theme setup (for CLI)"""
        # This would be called from CLI to set up custom themes
        # For now, save default themes to file
        themes_file = Path(self.settings.config_dir) / "themes.json"
        themes_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(themes_file, 'w') as f:
            json.dump(self.themes, f, indent=2)
        
        logger.info(f"Themes saved to {themes_file}")
        return list(self.themes.keys())
    
    def get_theme_statistics(self) -> Dict[str, Any]:
        """Get statistics about content themes"""
        # This would query the database for theme usage statistics
        stats = {}
        
        for theme in self.themes:
            # Get count of videos generated for this theme
            # This is a simplified version - would need proper DB query
            stats[theme] = {
                "total_generated": 0,
                "successful_posts": 0,
                "average_engagement": 0.0
            }
        
        return stats
    
    async def get_trending_hashtags(self) -> List[str]:
        """Get currently trending hashtags (would integrate with TikTok API)"""
        # This is a placeholder - would integrate with TikTok's research API
        # or use web scraping to get trending hashtags
        
        trending = [
            "#fyp", "#foryou", "#viral", "#trending", "#explore",
            "#motivation", "#success", "#inspiration", "#mindset",
            "#love", "#life", "#happiness", "#positive", "#goals"
        ]
        
        return random.sample(trending, 5)
    
    def create_content_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """Create content calendar for upcoming days"""
        calendar = []
        themes = list(self.themes.keys())
        
        for day in range(days):
            daily_posts = []
            
            for _ in range(self.settings.daily_post_count):
                theme = random.choice(themes)
                
                # Schedule posts at optimal times
                for post_time in self.settings.post_times_list:
                    daily_posts.append({
                        "theme": theme,
                        "scheduled_time": post_time,
                        "status": "planned"
                    })
            
            calendar.append({
                "day": day + 1,
                "posts": daily_posts[:self.settings.daily_post_count]
            })
        
        return calendar