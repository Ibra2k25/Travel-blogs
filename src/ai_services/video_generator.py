"""
AI Video Generation Service
Integrates with multiple AI video generation APIs
"""

import asyncio
import time
import random
from typing import Optional, Dict, Any, List
from pathlib import Path
import aiohttp
import httpx
from ..config import get_settings
from ..logger import setup_logger, log_async_performance, log_video_generation
from ..database import get_db_ops

logger = setup_logger(__name__)

class AIVideoGenerator:
    """Main AI video generation service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_ops = get_db_ops()
        self.services = {
            "runway": RunwayService(self.settings),
            "pika": PikaService(self.settings),
            "kling": KlingService(self.settings),
            "minimax": MinimaxService(self.settings),
            "luma": LumaService(self.settings),
            "aiml": AIMLService(self.settings)  # Unified API
        }
        self.preferred_services = ["aiml", "runway", "kling", "pika"]
    
    @log_async_performance
    async def generate_video(
        self,
        prompt: str,
        theme: str = "motivational",
        style: str = "cinematic",
        duration: int = 10,
        aspect_ratio: str = "9:16",
        service: Optional[str] = None
    ) -> str:
        """Generate video using AI service"""
        
        # Create database record
        video_gen = self.db_ops.create_video_generation(
            service=service or "auto",
            prompt=prompt,
            theme=theme,
            style=style,
            duration=duration,
            aspect_ratio=aspect_ratio,
            status="pending"
        )
        
        start_time = time.time()
        
        try:
            # Auto-select service if not specified
            if not service:
                service = await self._select_best_service()
            
            logger.info(f"Generating video with {service} service")
            
            # Generate video
            video_path = await self._generate_with_service(
                service, prompt, theme, style, duration, aspect_ratio
            )
            
            # Get file size
            file_size = Path(video_path).stat().st_size if Path(video_path).exists() else 0
            generation_time = time.time() - start_time
            
            # Update database record
            self.db_ops.update_video_generation(
                video_gen.id,
                status="success",
                video_path=video_path,
                generation_time=generation_time,
                file_size=file_size
            )
            
            log_video_generation(
                service=service,
                prompt=prompt,
                duration=duration,
                status="success",
                execution_time=generation_time
            )
            
            return video_path
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_message = str(e)
            
            # Update database record
            self.db_ops.update_video_generation(
                video_gen.id,
                status="failed",
                error_message=error_message,
                generation_time=generation_time
            )
            
            log_video_generation(
                service=service or "unknown",
                prompt=prompt,
                duration=duration,
                status="failed",
                execution_time=generation_time,
                error=error_message
            )
            
            logger.error(f"Video generation failed: {e}")
            raise
    
    async def _select_best_service(self) -> str:
        """Select the best available AI service"""
        # Check which services have API keys
        available_services = []
        
        for service_name in self.preferred_services:
            if self._is_service_available(service_name):
                available_services.append(service_name)
        
        if not available_services:
            raise ValueError("No AI video generation services available. Please configure API keys.")
        
        # For now, return the first available service
        # In future, could implement load balancing, cost optimization, etc.
        return available_services[0]
    
    def _is_service_available(self, service_name: str) -> bool:
        """Check if service is available (has API key)"""
        api_keys = self.settings.validate_api_keys()
        
        if service_name == "aiml":
            return api_keys.get("aiml", False)
        elif service_name == "runway":
            return api_keys.get("runway", False) or api_keys.get("aiml", False)
        elif service_name == "pika":
            return api_keys.get("pika", False) or api_keys.get("aiml", False)
        elif service_name == "kling":
            return api_keys.get("kling", False) or api_keys.get("aiml", False)
        elif service_name == "minimax":
            return api_keys.get("minimax", False) or api_keys.get("aiml", False)
        elif service_name == "luma":
            return api_keys.get("luma", False) or api_keys.get("aiml", False)
        
        return False
    
    async def _generate_with_service(
        self,
        service: str,
        prompt: str,
        theme: str,
        style: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Generate video with specific service"""
        if service not in self.services:
            raise ValueError(f"Unknown service: {service}")
        
        generator = self.services[service]
        
        return await generator.generate(
            prompt=prompt,
            theme=theme,
            style=style,
            duration=duration,
            aspect_ratio=aspect_ratio
        )
    
    async def test_service(self, service: str) -> str:
        """Test specific AI service"""
        test_prompt = "A beautiful sunset over mountains, cinematic style"
        
        return await self._generate_with_service(
            service=service,
            prompt=test_prompt,
            theme="nature",
            style="cinematic",
            duration=5,
            aspect_ratio="9:16"
        )

class BaseVideoService:
    """Base class for AI video services"""
    
    def __init__(self, settings):
        self.settings = settings
        self.timeout = 300  # 5 minutes default timeout
    
    async def generate(
        self,
        prompt: str,
        theme: str,
        style: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Generate video - to be implemented by subclasses"""
        raise NotImplementedError
    
    def _get_output_path(self) -> str:
        """Generate unique output file path"""
        timestamp = int(time.time())
        random_id = random.randint(1000, 9999)
        filename = f"video_{timestamp}_{random_id}.mp4"
        return str(Path(self.settings.videos_dir) / filename)

class AIMLService(BaseVideoService):
    """AI/ML API unified service"""
    
    async def generate(
        self,
        prompt: str,
        theme: str,
        style: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Generate video using AI/ML API"""
        
        if not self.settings.aiml_api_key:
            raise ValueError("AI/ML API key not configured")
        
        # Use Runway Gen-4 Turbo through AI/ML API
        url = "https://api.aimlapi.com/v1/video/generations"
        
        headers = {
            "Authorization": f"Bearer {self.settings.aiml_api_key}",
            "Content-Type": "application/json"
        }
        
        # Enhance prompt based on theme and style
        enhanced_prompt = self._enhance_prompt(prompt, theme, style)
        
        payload = {
            "model": "gen4_turbo",
            "prompt": enhanced_prompt,
            "duration": duration,
            "ratio": aspect_ratio,
            "seed": random.randint(1, 1000000)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            
            # Poll for completion if needed
            if "id" in result:
                video_url = await self._poll_for_completion(result["id"], headers)
            else:
                video_url = result.get("video_url")
            
            if not video_url:
                raise ValueError("No video URL returned from AI/ML API")
            
            # Download video
            return await self._download_video(video_url)
    
    async def _poll_for_completion(self, generation_id: str, headers: dict) -> str:
        """Poll API for video completion"""
        poll_url = f"https://api.aimlapi.com/v1/video/generations/{generation_id}"
        
        max_polls = 60  # 5 minutes max
        poll_interval = 5  # 5 seconds
        
        for _ in range(max_polls):
            async with httpx.AsyncClient() as client:
                response = await client.get(poll_url, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                status = result.get("status")
                
                if status == "completed":
                    return result.get("video_url")
                elif status == "failed":
                    raise ValueError(f"Video generation failed: {result.get('error', 'Unknown error')}")
                
                await asyncio.sleep(poll_interval)
        
        raise TimeoutError("Video generation timed out")
    
    async def _download_video(self, video_url: str) -> str:
        """Download generated video"""
        output_path = self._get_output_path()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url)
            response.raise_for_status()
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(response.content)
        
        return output_path
    
    def _enhance_prompt(self, prompt: str, theme: str, style: str) -> str:
        """Enhance prompt based on theme and style"""
        enhancements = {
            "motivational": "inspirational, uplifting, energetic, powerful",
            "educational": "clear, informative, professional, engaging",
            "trending": "viral, popular, current, engaging",
            "abstract": "artistic, creative, unique, experimental",
            "nature": "natural, serene, beautiful, organic",
            "urban": "modern, cityscape, dynamic, contemporary"
        }
        
        style_enhancements = {
            "cinematic": "cinematic lighting, film quality, professional cinematography",
            "realistic": "photorealistic, high detail, natural lighting",
            "artistic": "artistic style, creative composition, unique perspective",
            "dramatic": "dramatic lighting, high contrast, intense mood"
        }
        
        enhanced = prompt
        
        if theme in enhancements:
            enhanced += f", {enhancements[theme]}"
        
        if style in style_enhancements:
            enhanced += f", {style_enhancements[style]}"
        
        enhanced += ", high quality, 4K resolution, vertical aspect ratio"
        
        return enhanced

class RunwayService(BaseVideoService):
    """Runway ML service"""
    
    async def generate(
        self,
        prompt: str,
        theme: str,
        style: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Generate video using Runway API"""
        
        if not self.settings.runway_api_key:
            # Fall back to AI/ML API if direct Runway key not available
            if self.settings.aiml_api_key:
                aiml_service = AIMLService(self.settings)
                return await aiml_service.generate(prompt, theme, style, duration, aspect_ratio)
            else:
                raise ValueError("Runway API key not configured")
        
        # Direct Runway API implementation would go here
        # For now, using AI/ML API as fallback
        aiml_service = AIMLService(self.settings)
        return await aiml_service.generate(prompt, theme, style, duration, aspect_ratio)

class PikaService(BaseVideoService):
    """Pika Labs service"""
    
    async def generate(
        self,
        prompt: str,
        theme: str,
        style: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Generate video using Pika API"""
        
        # Implementation would use Pika's API
        # For now, falling back to AI/ML API
        aiml_service = AIMLService(self.settings)
        return await aiml_service.generate(prompt, theme, style, duration, aspect_ratio)

class KlingService(BaseVideoService):
    """Kling AI service"""
    
    async def generate(
        self,
        prompt: str,
        theme: str,
        style: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Generate video using Kling API"""
        
        # Implementation would use Kling's API
        # For now, falling back to AI/ML API
        aiml_service = AIMLService(self.settings)
        return await aiml_service.generate(prompt, theme, style, duration, aspect_ratio)

class MinimaxService(BaseVideoService):
    """MiniMax service"""
    
    async def generate(
        self,
        prompt: str,
        theme: str,
        style: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Generate video using MiniMax API"""
        
        # Implementation would use MiniMax's API
        # For now, falling back to AI/ML API
        aiml_service = AIMLService(self.settings)
        return await aiml_service.generate(prompt, theme, style, duration, aspect_ratio)

class LumaService(BaseVideoService):
    """Luma AI service"""
    
    async def generate(
        self,
        prompt: str,
        theme: str,
        style: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Generate video using Luma API"""
        
        # Implementation would use Luma's API
        # For now, falling back to AI/ML API
        aiml_service = AIMLService(self.settings)
        return await aiml_service.generate(prompt, theme, style, duration, aspect_ratio)