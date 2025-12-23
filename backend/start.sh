#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "================================================"
echo "🔄 Disha AI Backend - Startup Script"
echo "================================================"

# Change to the backend directory (works both locally and on Render)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Current directory: $(pwd)"
echo "🔍 Listing files:"
ls -la

echo ""
echo "🗄️  Initializing database..."
echo "================================================"

# Run database initialization with error handling
if python app/init_db.py; then
    echo "✅ Database initialized successfully!"
else
    echo "❌ Database initialization failed!"
    echo "⚠️  Continuing anyway - tables might already exist"
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "================================================"

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
