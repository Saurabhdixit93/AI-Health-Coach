#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "================================================"
echo "🔄 Disha AI Backend - Startup Script"
echo "================================================"

# Change to the backend directory (works both locally and on Render)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Current directory: $(pwd)"

# Set PYTHONPATH so Python can find the app module
export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}"
echo "🐍 PYTHONPATH: $PYTHONPATH"

echo ""
echo "🗄️  Initializing database..."
echo "================================================"

# Run database initialization as a Python module
if python -m app.init_db; then
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
