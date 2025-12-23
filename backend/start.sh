#!/bin/bash
# Startup script for Render deployment

echo "🔄 Checking database initialization..."

# Run database initialization (creates tables if they don't exist)
cd /opt/render/project/src/backend
python app/init_db.py

echo "✅ Database ready!"
echo "🚀 Starting uvicorn server..."

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port $PORT
