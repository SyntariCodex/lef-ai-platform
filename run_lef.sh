#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down LEF system...${NC}"
    pkill -f "python.*lef" || true
    exit 0
}

# Register cleanup handler
trap cleanup EXIT INT TERM

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Create necessary directories
mkdir -p ~/.lef/logs ~/.lef/state

# Clear the screen and show startup message
clear
echo -e "${BLUE}🚀 Launching LEF System...${NC}"

# Kill any existing LEF processes
echo -e "${BLUE}Cleaning up old processes...${NC}"
pkill -f "python.*lef" || true
sleep 1  # Give processes time to die

# Start the supervisor in the foreground
echo -e "${GREEN}Starting LEF Supervisor...${NC}"
exec python3 -m src.lef.supervisor

# The supervisor will handle:
# 1. Starting the main LEF system
# 2. Starting the progress monitor
# 3. Managing the bridge layer
# 4. Auto-restarting components if they crash 