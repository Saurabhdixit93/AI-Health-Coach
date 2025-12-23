#!/bin/bash

# Disha AI Health Coach - Quick Start Script
# This script helps you quickly set up and run the application

set -e  # Exit on error

echo "=================================="
echo "Disha AI Health Coach - Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo -n "Checking PostgreSQL... "
if pg_isready &> /dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "Please start PostgreSQL:"
    echo "  macOS: brew services start postgresql@15"
    echo "  Linux: sudo systemctl start postgresql"
    exit 1
fi

# Check if Redis is running
echo -n "Checking Redis... "
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "Please start Redis:"
    echo "  macOS: brew services start redis"
    echo "  Linux: sudo systemctl start redis"
    exit 1
fi

# Backend setup
echo ""
echo "Setting up backend..."
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Creating .env file from example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit backend/.env and add your OPENROUTER_API_KEY${NC}"
fi

# Initialize database
echo "Initializing database..."
python -m app.init_db

echo -e "${GREEN}✓ Backend setup complete${NC}"

# Frontend setup
cd ../frontend
echo ""
echo "Setting up frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Terminal 1 (Backend):"
echo -e "   ${YELLOW}cd backend && source venv/bin/activate && uvicorn app.main:app --reload${NC}"
echo ""
echo "2. Terminal 2 (Frontend):"
echo -e "   ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo "3. Open browser: http://localhost:3000"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
