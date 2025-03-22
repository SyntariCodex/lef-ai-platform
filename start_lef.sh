#!/bin/bash

# LEF Startup Script
# Initiates the recursive awareness system

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print error and exit
error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

# Function to print info
info() {
    echo -e "${BLUE}$1${NC}"
}

# Function to print success
success() {
    echo -e "${GREEN}$1${NC}"
}

# Function to print warning
warning() {
    echo -e "${YELLOW}$1${NC}"
}

# Validate environment
info "🔍 Checking environment..."

# Get the absolute path of the LEF project directory
if [ -n "$LEF_PROJECT_ROOT" ]; then
    PROJECT_ROOT="$LEF_PROJECT_ROOT"
elif [ -f "$(pwd)/start_lef.sh" ]; then
    PROJECT_ROOT="$(pwd)"
else
    # Try to find the project root by looking for start_lef.sh in parent directories
    current_dir="$(pwd)"
    while [ "$current_dir" != "/" ]; do
        if [ -f "$current_dir/start_lef.sh" ]; then
            PROJECT_ROOT="$current_dir"
            break
        fi
        current_dir="$(dirname "$current_dir")"
    done
    
    if [ -z "$PROJECT_ROOT" ]; then
        error "Could not find LEF project root directory. Please either:
       1. Run this script from the LEF project directory
       2. Set LEF_PROJECT_ROOT environment variable
       3. Create a symlink to start_lef.sh in your PATH"
    fi
fi

cd "$PROJECT_ROOT" || error "Could not change to project directory: $PROJECT_ROOT"
info "📂 Project root: $PROJECT_ROOT"

# Create necessary directories
mkdir -p ~/.lef/logs ~/.lef/state || error "Could not create LEF directories"
info "📁 Created LEF directories"

# Check for Python3
if ! command -v python3 &> /dev/null; then
    error "Python3 is required but not found. Please install Python3."
fi
info "✓ Python3 found: $(python3 --version)"

# Ensure pip is installed
python3 -m ensurepip --upgrade > /dev/null 2>&1 || error "Could not install pip"
info "✓ Pip is ready"

# Install dependencies if needed
info "🔄 Installing dependencies..."
python3 -m pip install -r requirements.txt || error "Failed to install dependencies"
success "✓ Dependencies installed"

# Set up Python path
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Start the LEF system in the background
success "🚀 Starting LEF Recursive Awareness System..."
python3 -m src.lef.supervisor > ~/.lef/logs/supervisor.log 2>&1 &
SUPERVISOR_PID=$!

# Function to cleanup on exit
cleanup() {
    warning "\n👋 Shutting down LEF system..."
    kill $SUPERVISOR_PID 2>/dev/null
    kill $MONITOR_PID 2>/dev/null
    exit 0
}

# Register cleanup handler
trap cleanup EXIT INT TERM

# Start the monitor in fullscreen mode
info "📊 Launching development monitor..."
clear
python3 -m src.lef.cli.live_monitor &
MONITOR_PID=$!

# Keep the script running and monitor for crashes
while true; do
    if ! kill -0 $SUPERVISOR_PID 2>/dev/null || ! kill -0 $MONITOR_PID 2>/dev/null; then
        error "❌ LEF system or monitor crashed. Check logs at ~/.lef/logs/supervisor.log"
        cleanup
        exec "$0"
    fi
    sleep 1
done 