#!/bin/bash

# Todo App - Stop Local Servers Script

echo "🛑 Stopping Todo App servers..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Stop by PID files
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}✓ Backend stopped (PID: $BACKEND_PID)${NC}"
    fi
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✓ Frontend stopped (PID: $FRONTEND_PID)${NC}"
    fi
    rm .frontend.pid
fi

# Fallback: kill by process name
pkill -f "uvicorn src.main:app" 2>/dev/null && echo -e "${GREEN}✓ Killed uvicorn processes${NC}"
pkill -f "next dev" 2>/dev/null && echo -e "${GREEN}✓ Killed Next.js processes${NC}"

echo ""
echo -e "${GREEN}All servers stopped!${NC}"
