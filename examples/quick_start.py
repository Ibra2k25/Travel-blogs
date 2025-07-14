#!/usr/bin/env python3
"""
TikTok AI Bot - Quick Start Example
This script demonstrates how to use the TikTok AI Bot
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.bot import TikTokBot
from src.config import get_settings

async def main():
    """Quick start example"""
    
    print("🤖 TikTok AI Bot - Quick Start Example")
    print("=====================================")
    
    # Initialize the bot
    async with TikTokBot() as bot:
        
        # Check configuration
        settings = get_settings()
        api_keys = settings.validate_api_keys()
        
        print(f"\n📋 Configuration Status:")
        print(f"   AI/ML API: {'✅' if api_keys['aiml'] else '❌'}")
        print(f"   OpenAI API: {'✅' if api_keys['openai'] else '❌'}")
        print(f"   TikTok Username: {settings.tiktok_username or '❌ Not configured'}")
        
        if not any(api_keys.values()):
            print("\n❌ No AI services configured!")
            print("Please add your API keys to the .env file:")
            print("   AIML_API_KEY=your_key_here")
            print("   OPENAI_API_KEY=your_key_here")
            return
        
        # Test services
        print("\n🧪 Testing Services...")
        test_results = await bot.test_services()
        
        for service, result in test_results.items():
            status = "✅" if result.get("status") == "success" else "❌"
            print(f"   {service}: {status}")
            if result.get("status") == "failed":
                print(f"      Error: {result.get('error', 'Unknown error')}")
        
        # Check if we can proceed
        if test_results.get("ai_generation", {}).get("status") != "success":
            print("\n❌ AI video generation not working. Please check your API keys.")
            return
        
        print("\n🎬 Generating a test video...")
        
        try:
            # Generate a video
            video_path = await bot.generate_video(
                theme="motivational",
                style="cinematic",
                duration=5  # Short test video
            )
            
            print(f"✅ Video generated successfully: {video_path}")
            
            # Check if TikTok account is configured
            if settings.tiktok_username:
                print(f"\n📱 TikTok account configured: {settings.tiktok_username}")
                
                # Ask if user wants to upload
                upload = input("Do you want to upload this video to TikTok? (y/N): ").strip().lower()
                
                if upload == 'y':
                    print("🚀 Uploading to TikTok...")
                    
                    try:
                        result = await bot.post_video(video_path)
                        
                        if result['success']:
                            print("✅ Video uploaded successfully!")
                        else:
                            print(f"❌ Upload failed: {result.get('error')}")
                    
                    except Exception as e:
                        print(f"❌ Upload error: {e}")
                        print("Note: You may need to configure TikTok cookies first.")
                        print("Run: python main.py add-account")
            else:
                print("\n📱 TikTok account not configured.")
                print("To upload videos, run: python main.py add-account")
            
            # Show queue status
            queue_status = bot.get_queue_status()
            print(f"\n📦 Videos in queue: {len(queue_status)}")
            
            # Show statistics
            stats = bot.get_statistics()
            print(f"\n📊 Bot Statistics:")
            print(f"   Videos generated: {stats.get('videos_generated', 0)}")
            print(f"   Total posts: {stats.get('total_posts', 0)}")
            print(f"   Success rate: {stats.get('success_rate', 0):.1f}%")
            
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            return
        
        print("\n🎉 Quick start completed!")
        print("\nNext steps:")
        print("1. Configure your .env file with API keys")
        print("2. Add TikTok account: python main.py add-account")
        print("3. Start automated posting: python main.py start-scheduler")
        print("4. Generate more videos: python main.py generate-queue --count 10")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)