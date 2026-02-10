#!/bin/bash

# Todo App - Local Development Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting Todo App (Local Development)..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}📁 Project Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $(python3 --version | cut -d' ' -f2)${NC}"
echo -e "${GREEN}✓ Node $(node --version)${NC}"
echo ""

# Backend setup
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}Backend Setup${NC}"
echo -e "${BLUE}==================================================${NC}"

cd "$SCRIPT_DIR/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./test.db
BETTER_AUTH_SECRET=test-secret-key-with-at-least-32-characters-for-jwt-signing
EOF
fi

# Initialize database if not exists
if [ ! -f "test.db" ]; then
    echo "Initializing database..."
    python init_db.py
fi

# Start backend in background
echo -e "${GREEN}Starting backend server...${NC}"
nohup uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "${GREEN}  URL: http://localhost:8000${NC}"
echo -e "${GREEN}  Logs: backend/backend.log${NC}"

# Give backend time to start
sleep 3

# Frontend setup
echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}Frontend Setup${NC}"
echo -e "${BLUE}==================================================${NC}"

cd "$SCRIPT_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
fi

# Check if postcss.config.js exists
if [ ! -f "postcss.config.js" ]; then
    echo "Creating postcss.config.js..."
    cat > postcss.config.js << EOF
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF
fi

# Start frontend in background
echo -e "${GREEN}Starting frontend server...${NC}"
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "${GREEN}  URL: http://localhost:3000${NC}"
echo -e "${GREEN}  Logs: frontend/frontend.log${NC}"

# Wait for frontend to compile
echo ""
echo -e "${YELLOW}Waiting for frontend to compile (this may take 20-30 seconds)...${NC}"
sleep 25

# Summary
echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}✨ Todo App is Running!${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}To stop the servers:${NC}"
echo -e "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Or use:${NC}"
echo -e "  pkill -f 'uvicorn src.main:app'"
echo -e "  pkill -f 'next dev'"
echo ""
echo -e "${GREEN}🎉 Open your browser and go to: http://localhost:3000${NC}"
echo ""

# Save PIDs for later
echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"

echo "PIDs saved to .backend.pid and .frontend.pid"
