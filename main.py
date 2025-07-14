#!/usr/bin/env python3
"""
TikTok AI Video Bot - Main Entry Point
Automates video generation and posting to TikTok using AI services
"""

import asyncio
import click
import sys
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.bot import TikTokBot
from src.config import Settings
from src.logger import setup_logger
from src.database import init_database

console = Console()
logger = setup_logger(__name__)

# ASCII Art Banner
BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                    TikTok AI Video Bot                       ║
║                                                              ║
║  🤖 Automated Video Generation & Posting for TikTok 🎥     ║
╚══════════════════════════════════════════════════════════════╝
"""

def display_banner():
    """Display the application banner"""
    console.print(BANNER, style="bold blue")

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """TikTok AI Video Bot - Automated content creation and posting"""
    display_banner()

@cli.command()
@click.option('--theme', default='motivational', help='Content theme for video generation')
@click.option('--duration', default=10, help='Video duration in seconds')
@click.option('--style', default='cinematic', help='Video style')
@click.option('--post-now', is_flag=True, help='Post immediately after generation')
async def generate(theme: str, duration: int, style: str, post_now: bool):
    """Generate a single AI video"""
    console.print(f"🎬 Generating video with theme: {theme}", style="bold green")
    
    bot = TikTokBot()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating video...", total=None)
            
            video_path = await bot.generate_video(
                theme=theme,
                duration=duration,
                style=style
            )
            
            progress.update(task, description="✅ Video generated successfully!")
            
        console.print(f"📁 Video saved to: {video_path}", style="bold blue")
        
        if post_now:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            )
            
            with progress:
                task = progress.add_task("Posting to TikTok...", total=None)
                
                result = await bot.post_video(video_path)
                
                if result['success']:
                    progress.update(task, description="✅ Posted successfully!")
                    console.print("🚀 Video posted to TikTok!", style="bold green")
                else:
                    progress.update(task, description="❌ Failed to post")
                    console.print(f"Error: {result['error']}", style="bold red")
                    
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        logger.error(f"Video generation failed: {e}")

@cli.command()
@click.option('--count', default=5, help='Number of videos to generate for queue')
@click.option('--theme', default=None, help='Specific theme (random if not specified)')
def generate_queue(count: int, theme: Optional[str]):
    """Generate multiple videos for the posting queue"""
    console.print(f"📦 Generating {count} videos for queue...", style="bold cyan")
    
    asyncio.run(_generate_queue_async(count, theme))

async def _generate_queue_async(count: int, theme: Optional[str]):
    """Async implementation of queue generation"""
    bot = TikTokBot()
    
    with Progress() as progress:
        task = progress.add_task("Generating videos...", total=count)
        
        for i in range(count):
            try:
                video_path = await bot.generate_video(theme=theme)
                bot.content_manager.add_to_queue(video_path)
                progress.update(task, advance=1, description=f"Generated {i+1}/{count} videos")
                
            except Exception as e:
                console.print(f"❌ Failed to generate video {i+1}: {e}", style="red")
                
    console.print("✅ Queue generation completed!", style="bold green")

@cli.command()
@click.option('--daemon', is_flag=True, help='Run as background daemon')
def start_scheduler(daemon: bool):
    """Start the automated posting scheduler"""
    console.print("🕒 Starting TikTok posting scheduler...", style="bold cyan")
    
    if daemon:
        console.print("Running in daemon mode (background process)")
    
    asyncio.run(_start_scheduler_async(daemon))

async def _start_scheduler_async(daemon: bool):
    """Async implementation of scheduler"""
    bot = TikTokBot()
    
    try:
        await bot.start_scheduler(daemon=daemon)
    except KeyboardInterrupt:
        console.print("\n⏹️  Scheduler stopped by user", style="yellow")
    except Exception as e:
        console.print(f"❌ Scheduler error: {e}", style="bold red")
        logger.error(f"Scheduler failed: {e}")

@cli.command()
def add_account():
    """Add a new TikTok account"""
    console.print("➕ Adding new TikTok account...", style="bold cyan")
    
    username = click.prompt("Enter TikTok username")
    cookies_file = click.prompt("Enter path to cookies file", default="cookies/cookies.txt")
    
    bot = TikTokBot()
    
    try:
        success = bot.add_account(username, cookies_file)
        
        if success:
            console.print("✅ Account added successfully!", style="bold green")
        else:
            console.print("❌ Failed to add account", style="bold red")
            
    except Exception as e:
        console.print(f"❌ Error adding account: {e}", style="bold red")

@cli.command()
def list_accounts():
    """List all configured TikTok accounts"""
    bot = TikTokBot()
    accounts = bot.list_accounts()
    
    if not accounts:
        console.print("No accounts configured.", style="yellow")
        return
    
    table = Table(title="TikTok Accounts")
    table.add_column("Username", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Last Used", style="yellow")
    
    for account in accounts:
        table.add_row(
            account['username'],
            account['status'],
            account['last_used']
        )
    
    console.print(table)

@cli.command()
def show_queue():
    """Show current video queue"""
    bot = TikTokBot()
    queue = bot.content_manager.get_queue_status()
    
    table = Table(title="Video Queue")
    table.add_column("Position", style="cyan")
    table.add_column("Theme", style="green")
    table.add_column("Duration", style="yellow")
    table.add_column("Created", style="blue")
    
    for i, video in enumerate(queue, 1):
        table.add_row(
            str(i),
            video['theme'],
            f"{video['duration']}s",
            video['created']
        )
    
    console.print(table)

@cli.command()
def show_stats():
    """Show bot statistics and analytics"""
    bot = TikTokBot()
    stats = bot.get_statistics()
    
    # Create stats display
    table = Table(title="TikTok Bot Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Videos Generated", str(stats['videos_generated']))
    table.add_row("Total Posts", str(stats['total_posts']))
    table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
    table.add_row("Queue Size", str(stats['queue_size']))
    table.add_row("Active Accounts", str(stats['active_accounts']))
    
    console.print(table)

@cli.command()
def setup_themes():
    """Setup and configure content themes"""
    console.print("🎨 Setting up content themes...", style="bold cyan")
    
    bot = TikTokBot()
    themes = bot.content_manager.setup_themes_interactive()
    
    console.print(f"✅ Configured {len(themes)} themes", style="bold green")

@cli.command()
@click.option('--service', default='runway', help='AI service to test')
def test_generation(service: str):
    """Test AI video generation service"""
    console.print(f"🧪 Testing {service} video generation...", style="bold cyan")
    
    asyncio.run(_test_generation_async(service))

async def _test_generation_async(service: str):
    """Async test of video generation"""
    bot = TikTokBot()
    
    try:
        video_path = await bot.ai_generator.test_service(service)
        console.print(f"✅ Test successful! Video: {video_path}", style="bold green")
    except Exception as e:
        console.print(f"❌ Test failed: {e}", style="bold red")

@cli.command()
def clean_cache():
    """Clean temporary files and cache"""
    console.print("🧹 Cleaning cache and temporary files...", style="bold cyan")
    
    bot = TikTokBot()
    cleaned_files = bot.clean_cache()
    
    console.print(f"✅ Cleaned {cleaned_files} files", style="bold green")

@cli.command()
@click.argument('config_file')
def load_config(config_file: str):
    """Load configuration from file"""
    console.print(f"⚙️  Loading configuration from {config_file}...", style="bold cyan")
    
    bot = TikTokBot()
    
    try:
        bot.load_config(config_file)
        console.print("✅ Configuration loaded successfully!", style="bold green")
    except Exception as e:
        console.print(f"❌ Failed to load config: {e}", style="bold red")

# Quick action commands
@cli.command(name='post-now')
async def post_now():
    """Generate and post a video immediately"""
    console.print("🚀 Quick post: Generating and posting now...", style="bold cyan")
    
    bot = TikTokBot()
    
    try:
        # Generate video
        video_path = await bot.generate_video()
        console.print("✅ Video generated!", style="green")
        
        # Post immediately
        result = await bot.post_video(video_path)
        
        if result['success']:
            console.print("🎉 Video posted successfully!", style="bold green")
        else:
            console.print(f"❌ Failed to post: {result['error']}", style="bold red")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")

if __name__ == "__main__":
    # Initialize database on startup
    init_database()
    
    # Handle async commands
    import inspect
    
    # Monkey patch click to handle async functions
    original_invoke = click.Command.invoke
    
    def invoke_async(self, ctx):
        if inspect.iscoroutinefunction(self.callback):
            return asyncio.run(self.callback(**ctx.params))
        else:
            return original_invoke(self, ctx)
    
    click.Command.invoke = invoke_async
    
    # Run CLI
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="bold yellow")
    except Exception as e:
        console.print(f"❌ Fatal error: {e}", style="bold red")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)