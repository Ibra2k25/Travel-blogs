#!/bin/bash

# TikTok AI Video Bot Installation Script
# Automates the setup process for the TikTok bot

set -e  # Exit on any error

echo "🤖 TikTok AI Video Bot - Installation Script"
echo "============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# Check system requirements
print_status "Checking system requirements..."

PYTHON_REQUIRED=0
NODE_REQUIRED=0
FFMPEG_REQUIRED=0

if ! check_command python3; then
    PYTHON_REQUIRED=1
fi

if ! check_command node; then
    NODE_REQUIRED=1
fi

if ! check_command ffmpeg; then
    FFMPEG_REQUIRED=1
fi

if ! check_command npm; then
    print_error "npm is not installed (usually comes with Node.js)"
    NODE_REQUIRED=1
fi

# Install missing dependencies
if [ $PYTHON_REQUIRED -eq 1 ] || [ $NODE_REQUIRED -eq 1 ] || [ $FFMPEG_REQUIRED -eq 1 ]; then
    print_warning "Some dependencies are missing. Attempting to install..."
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Detected Linux system"
        
        if [ $PYTHON_REQUIRED -eq 1 ]; then
            print_status "Installing Python3..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip
        fi
        
        if [ $NODE_REQUIRED -eq 1 ]; then
            print_status "Installing Node.js..."
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        fi
        
        if [ $FFMPEG_REQUIRED -eq 1 ]; then
            print_status "Installing FFmpeg..."
            sudo apt-get install -y ffmpeg
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "Detected macOS system"
        
        if ! command -v brew &> /dev/null; then
            print_status "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        if [ $PYTHON_REQUIRED -eq 1 ]; then
            print_status "Installing Python3..."
            brew install python3
        fi
        
        if [ $NODE_REQUIRED -eq 1 ]; then
            print_status "Installing Node.js..."
            brew install node
        fi
        
        if [ $FFMPEG_REQUIRED -eq 1 ]; then
            print_status "Installing FFmpeg..."
            brew install ffmpeg
        fi
        
    else
        print_error "Unsupported operating system. Please install Python 3.9+, Node.js 18+, and FFmpeg manually."
        exit 1
    fi
fi

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

# Install Playwright browsers
print_status "Installing Playwright browsers..."
python -m playwright install

# Create necessary directories
print_status "Creating directories..."
mkdir -p generated_videos video_queue logs config data cookies

# Create example environment file
print_status "Creating example environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    print_warning "Please edit .env file with your API keys before running the bot"
fi

# Initialize database
print_status "Initializing database..."
python -c "from src.database import init_database; init_database()"

# Create config template
print_status "Creating configuration template..."
python -c "from src.config import save_config_template; save_config_template()"

print_success "Installation completed successfully!"
echo ""
echo "🎉 TikTok AI Video Bot is now installed!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your API keys:"
echo "   - Get AI/ML API key from: https://aimlapi.com"
echo "   - Add OpenAI API key for enhanced content generation"
echo "   - Configure TikTok account settings"
echo ""
echo "2. Add a TikTok account:"
echo "   python main.py add-account"
echo ""
echo "3. Test the installation:"
echo "   python main.py test-generation --service aiml"
echo ""
echo "4. Generate your first video:"
echo "   python main.py generate --theme motivational"
echo ""
echo "5. Start the automated scheduler:"
echo "   python main.py start-scheduler"
echo ""
echo "For more help, run: python main.py --help"
echo ""
print_warning "Remember to activate the virtual environment before running:"
print_warning "source venv/bin/activate"