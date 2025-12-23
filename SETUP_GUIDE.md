# Quick Setup Guide - Disha AI Health Coach

Your system needs Xcode Command Line Tools to create Python virtual environments.

## Solution: Manual Setup (5 minutes)

### Step 1: Install Xcode Command Line Tools

```bash
xcode-select --install
```

Click "Install" in the popup dialog. This will take 2-3 minutes.

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env
cp .env.example .env

# IMPORTANT: Edit .env file and verify the OPENROUTER_API_KEY is correct
nano .env  # or use: code .env

# Initialize database (creates tables and seeds data)
python -m app.init_db

# Start backend server
uvicorn app.main:app --reload
```

### Step 3: Frontend Setup (New Terminal Window)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

### Step 4: Open the App

Open your browser and go to: **http://localhost:3000**

---

## Verify It's Working

1. Backend should show: `Application startup complete`
2. Frontend should show: `Ready in X ms`
3. Browser should load the chat interface
4. API docs available at: http://localhost:8000/docs

---

## Already Installed Xcode Tools?

If you already have Xcode tools and want to use a simpler approach:

```bash
# Remove corrupted venv
rm -rf backend/venv

# Use the system's venv
cd backend
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.init_db
```

---

## Need Help?

Check the [README.md](README.md) for detailed troubleshooting.

The issue is that macOS ships with a stub `python3` that requires Xcode command line tools. Once installed, everything will work smoothly! 🚀
