#!/bin/bash

# ATLAS Startup Script
# Launches the autonomous business system

echo "============================================================"
echo " ATLAS AUTONOMOUS BUSINESS SYSTEM v2.0"
echo "============================================================"
echo " Starting all agents..."
echo "============================================================"

# Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "ERROR: Python 3 is required"
    exit 1
fi

# Check for required environment variables
ENV_FILE="config/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE not found"
    echo "Please create the environment file with required credentials"
    exit 1
fi

# Load environment variables
export $(cat $ENV_FILE | grep -v '^#' | xargs)

# Check critical variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set in .env"
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "ERROR: SUPABASE_URL not set in .env"
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip3 install -q fastapi uvicorn supabase anthropic schedule praw apify-client 2>/dev/null

# Kill any existing ATLAS processes
echo "Stopping any existing ATLAS processes..."
pkill -f "atlas_orchestrator.py" 2>/dev/null

# Start the orchestrator
echo "Starting ATLAS Orchestrator..."
python3 atlas_orchestrator.py &
ATLAS_PID=$!

echo "============================================================"
echo " ATLAS is running!"
echo " PID: $ATLAS_PID"
echo ""
echo " Endpoints:"
echo "   • http://localhost:8000/             - System info"
echo "   • http://localhost:8000/api/status   - Current status"
echo "   • http://localhost:8000/api/discover - Run discovery"
echo "   • http://localhost:8000/api/orchestrate - Run orchestration"
echo ""
echo " To stop: kill $ATLAS_PID"
echo "============================================================"

# Wait for process
wait $ATLAS_PID