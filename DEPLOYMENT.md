# Deployment Guide - Disha AI Health Coach

Complete guide to deploy Disha AI Health Coach for **FREE** using various cloud platforms.

---

## 📋 Table of Contents

- [Deployment Architecture](#deployment-architecture)
- [Option 1: All-in-One Deployment (Render.com)](#option-1-all-in-one-deployment-rendercom) ⭐ **Recommended**
- [Option 2: Separated Deployment (Vercel + Railway)](#option-2-separated-deployment-vercel--railway)
- [Option 3: Budget Deployment (Free Tier Mix)](#option-3-budget-deployment-free-tier-mix)
- [Environment Variables Setup](#environment-variables-setup)
- [Post-Deployment Checklist](#post-deployment-checklist)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## 🏗 Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Browser                      │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────-┐      ┌────────▼───────┐
│   Frontend      │      │    Backend     │
│   (Vercel)      │◄────►│   (Render)     │
│   Next.js       │      │   FastAPI      │
└─────────────────┘      └────────┬───────┘
                                  │
                         ┌────────┴────────┐
                         │                 │
                  ┌──────▼──────┐   ┌─────-▼─────┐
                  │ PostgreSQL  │   │   Redis    │
                  │  (Render)   │   │  (Upstash) │
                  └─────────────┘   └────────────┘
```

---

## Option 1: All-in-One Deployment (Render.com)

**⭐ RECOMMENDED for beginners** - Everything in one place, easiest to manage.

### What You Get (Free Tier)

- ✅ Backend (FastAPI)
- ✅ PostgreSQL Database
- ✅ Redis (via Upstash integration)
- ✅ Automatic HTTPS
- ❌ Frontend (use Vercel for this)

### Step 1: Prepare Your Code

1. **Create `render.yaml` in project root:**

```yaml
services:
  # Backend API
  - type: web
    name: disha-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: disha-db
          property: connectionString
      - key: REDIS_URL
        sync: false
      - key: OPENROUTER_API_KEY
        sync: false
      - key: AI_MODEL
        value: "openai/gpt-4o-mini"
      - key: AI_TEMPERATURE
        value: "0.7"
      - key: AI_MAX_TOKENS
        value: "500"
      - key: AI_BASE_URL
        value: "https://openrouter.ai/api/v1"
      - key: CORS_ORIGINS
        sync: false

databases:
  - name: disha-db
    databaseName: disha_db
    user: disha_user
    plan: free
```

2. **Update backend configuration** (if needed):

Create `backend/Procfile`:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

3. **Push to GitHub:**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/disha-ai.git
git push -u origin main
```

### Step 2: Deploy Backend on Render

1. **Sign up at [Render.com](https://render.com)** (free with GitHub)

2. **Create New PostgreSQL Database:**

   - Click "New +" → "PostgreSQL"
   - Name: `disha-db`
   - Database: `disha_db`
   - User: `disha_user`
   - Region: `Oregon (US West)`
   - Plan: **Free** (expires after 90 days, can recreate)
   - Click "Create Database"
   - **Save the connection string** (Internal Database URL)

3. **Create New Web Service:**

   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Name: `disha-backend`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

4. **Add Environment Variables:**

   - Go to "Environment" tab
   - Add these variables:
     ```
     DATABASE_URL = <paste Internal Database URL from PostgreSQL>
     REDIS_URL = <get from Upstash - see Step 3>
     OPENROUTER_API_KEY = sk-or-v1-your-api-key
     AI_PROVIDER = openai
     AI_MODEL = openai/gpt-4o-mini
     AI_TEMPERATURE = 0.7
     AI_MAX_TOKENS = 500
     AI_BASE_URL = https://openrouter.ai/api/v1
     APP_NAME = Disha AI Health Coach
     DEBUG = False
     CORS_ORIGINS = https://your-frontend-url.vercel.app
     ```

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for build to complete (~2-5 minutes)
   - Note your backend URL: `https://disha-backend.onrender.com`

### Step 3: Setup Redis on Upstash

1. **Sign up at [Upstash.com](https://upstash.com)** (free)

2. **Create Redis Database:**

   - Click "Create Database"
   - Name: `disha-redis`
   - Type: `Regional`
   - Region: `us-west-1` (closest to Render Oregon)
   - Plan: **Free** (10,000 commands/day)

3. **Get Connection URL:**

   - Copy the `UPSTASH_REDIS_REST_URL`
   - Go back to Render → Your Web Service → Environment
   - Update `REDIS_URL` with this URL

4. **Trigger redeploy:**
   - Go to "Manual Deploy" → "Deploy latest commit"

### Step 4: Initialize Database

1. **Open Render Shell:**

   - Go to your web service
   - Click "Shell" tab
   - Run: `python -m app.init_db`

2. **Verify:**
   - Visit: `https://disha-backend.onrender.com/api/health`
   - Should return `{"status": "healthy"}`

### Step 5: Deploy Frontend on Vercel

1. **Sign up at [Vercel.com](https://vercel.com)** (free with GitHub)

2. **Import Project:**

   - Click "New Project"
   - Import your GitHub repository
   - Root Directory: `frontend`
   - Framework: `Next.js`
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)

3. **Add Environment Variable:**

   - Add `NEXT_PUBLIC_API_URL` = `https://disha-backend.onrender.com`

4. **Deploy:**

   - Click "Deploy"
   - Wait for build (~2 minutes)
   - Your app will be live at: `https://your-project.vercel.app`

5. **Update Backend CORS:**
   - Go back to Render backend environment variables
   - Update `CORS_ORIGINS` to include your Vercel URL
   - Trigger manual redeploy

### Step 6: Test Deployment

1. Visit your Vercel URL
2. Try sending a message
3. Check if onboarding works
4. Test infinite scroll

✅ **Your app is now live!**

---

## Option 2: Separated Deployment (Vercel + Railway)

**Better for:** More reliable backend, PostgreSQL + Redis included.

### Railway.app Backend (PostgreSQL + Redis + Backend)

**Free Tier:** $5 credits/month (enough for hobby projects)

1. **Sign up at [Railway.app](https://railway.app)**

2. **Create New Project:**

   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

3. **Add PostgreSQL:**

   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Automatically provisions database
   - Connection string auto-added as `DATABASE_URL`

4. **Add Redis:**

   - Click "+ New" → "Database" → "Add Redis"
   - Connection string auto-added as `REDIS_URL`

5. **Configure Backend Service:**

   - Click on your service
   - Go to "Settings"
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. **Add Environment Variables:**

   - Click "Variables" tab
   - Add all variables (same as Render guide)

7. **Deploy & Initialize:**

   - Deployment starts automatically
   - Open terminal and run: `python -m app.init_db`

8. **Get Backend URL:**
   - Click "Settings" → "Networking" → "Generate Domain"
   - Copy the URL: `https://your-app.up.railway.app`

### Vercel Frontend (Same as Option 1, Step 5)

---

## Option 3: Budget Deployment (Free Tier Mix)

**Mix of free services for maximum uptime**

### Backend: Fly.io

- Free tier: 3 shared CPUs, 256MB RAM
- PostgreSQL: Fly Postgres (free tier available)

### Redis: Upstash

- Free tier: 10K commands/day

### Frontend: Vercel

- Free tier: Unlimited deployments

**Steps similar to Option 1, but consult respective documentation:**

- [Fly.io Docs](https://fly.io/docs/)
- [Upstash Docs](https://docs.upstash.com/)

---

## 🔐 Environment Variables Setup

### Backend Environment Variables

| Variable             | Description                  | Example                               |
| -------------------- | ---------------------------- | ------------------------------------- |
| `DATABASE_URL`       | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL`          | Redis connection string      | `redis://default:pass@host:6379`      |
| `OPENROUTER_API_KEY` | Your OpenRouter API key      | `sk-or-v1-...`                        |
| `AI_MODEL`           | Model to use                 | `openai/gpt-4o-mini`                  |
| `AI_TEMPERATURE`     | Response randomness          | `0.7`                                 |
| `AI_MAX_TOKENS`      | Max response length          | `500`                                 |
| `AI_BASE_URL`        | OpenRouter base URL          | `https://openrouter.ai/api/v1`        |
| `CORS_ORIGINS`       | Allowed frontend URLs        | `https://your-app.vercel.app`         |
| `APP_NAME`           | Application name             | `Disha AI Health Coach`               |
| `DEBUG`              | Debug mode                   | `False` (production)                  |

### Frontend Environment Variables

| Variable              | Description     | Example                             |
| --------------------- | --------------- | ----------------------------------- |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://your-backend.onrender.com` |

---

## ✅ Post-Deployment Checklist

After deploying, verify these:

### Backend Checks

- [ ] Health endpoint works: `GET /api/health`
- [ ] API docs accessible: `/docs`
- [ ] Database connected (check logs)
- [ ] Redis connected (check logs)
- [ ] LLM API key working (test a message)

### Frontend Checks

- [ ] Homepage loads
- [ ] Can create new user
- [ ] Can send messages
- [ ] Receives AI responses
- [ ] Infinite scroll works
- [ ] Typing indicator appears

### Integration Checks

- [ ] CORS configured correctly (no errors in console)
- [ ] Message timestamps correct
- [ ] Scroll-to-bottom button appears
- [ ] Protocol matching works (test "fever")

---

## 📊 Monitoring & Maintenance

### Free Monitoring Tools

1. **Render.com Dashboard:**

   - View logs
   - Monitor CPU/Memory usage
   - Check request metrics

2. **Vercel Analytics:**

   - Enable in Vercel dashboard
   - Track page views, performance

3. **UptimeRobot (Free):**
   - Sign up at [uptimerobot.com](https://uptimerobot.com)
   - Monitor your backend URL
   - Get alerts if down

### Logs

**Backend (Render):**

```bash
# View in dashboard or CLI
render logs -f <service-id>
```

**Frontend (Vercel):**

- View in Vercel dashboard under "Realtime" tab

### Database Backups

**Render PostgreSQL:**

- Free tier: No automatic backups
- Manual backup: Export via `pg_dump`

```bash
pg_dump $DATABASE_URL > backup.sql
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Backend won't start**

```
Error: Application startup failed
```

**Solution:**

- Check logs for Python errors
- Verify all environment variables are set
- Ensure `DATABASE_URL` and `REDIS_URL` are correct
- Check if database is accessible

#### 2. **Frontend can't connect to backend**

```
TypeError: Failed to fetch
```

**Solution:**

- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is running (visit `/api/health`)
- Check if backend URL is HTTPS (not HTTP)

#### 3. **Database connection timeout**

```
psycopg2.OperationalError: timeout
```

**Solution:**

- Render free tier can sleep after inactivity
- First request may be slow (wake-up time)
- Consider using paid tier for always-on

#### 4. **Redis connection failed**

```
redis.exceptions.ConnectionError
```

**Solution:**

- Check `REDIS_URL` format
- Verify Upstash database is active
- Check if firewall/IP restrictions apply

#### 5. **LLM API errors**

```
OpenAIError: Invalid API key
```

**Solution:**

- Verify `OPENROUTER_API_KEY` is correct
- Check OpenRouter dashboard for usage limits
- Ensure API key has credits

---

## 💡 Pro Tips

### Performance Optimization

1. **Use CDN for static assets** (Vercel does this automatically)
2. **Enable caching** in FastAPI responses
3. **Compress images** (if you add any)
4. **Use connection pooling** (already configured)

### Cost Optimization

1. **Render Free Tier** sleeps after 15min inactivity

   - First request takes ~30s to wake up
   - Use UptimeRobot to ping every 5min (keeps it awake)

2. **Database size limits:**

   - Render: 1GB free tier
   - Monitor with: `SELECT pg_database_size('disha_db');`

3. **Redis limits:**
   - Upstash: 10K commands/day free
   - Monitor in Upstash dashboard

### Security

1. **Never commit `.env` files**
2. **Rotate API keys** periodically
3. **Use HTTPS** everywhere (automatic on Render/Vercel)
4. **Monitor logs** for suspicious activity
5. **Enable rate limiting** (add in future)

---

## 🚀 Quick Deploy Commands

### One-Command Deploy (after setup)

```bash
# Backend (if using Railway)
railway up

# Frontend (if using Vercel)
vercel --prod

# Both (if using git push)
git push origin main  # Auto-deploys on Render & Vercel
```

---

## 📝 Important Notes

### Free Tier Limitations

| Platform          | Limitation            | Workaround                     |
| ----------------- | --------------------- | ------------------------------ |
| Render            | Sleeps after 15min    | Use ping service               |
| Render PostgreSQL | 90-day expiry         | Recreate database, backup data |
| Upstash Redis     | 10K commands/day      | Monitor usage                  |
| Vercel            | 100GB bandwidth/month | Unlikely to hit for small apps |

### Upgrade Paths

When you need more:

1. **Render Starter ($7/mo):**

   - No sleep
   - Always-on database
   - Better performance

2. **Railway Pro ($5/mo):**

   - More credits
   - Better support

3. **Upstash Pro ($10/mo):**
   - Unlimited commands
   - Better performance

---

## 🆘 Getting Help

1. **Check logs first** (90% of issues are in logs)
2. **Review this troubleshooting section**
3. **Platform-specific docs:**
   - [Render Docs](https://render.com/docs)
   - [Vercel Docs](https://vercel.com/docs)
   - [Railway Docs](https://docs.railway.app)
   - [Upstash Docs](https://docs.upstash.com)

---

## ✅ Deployment Complete!

Your Disha AI Health Coach is now live and accessible to the world! 🎉

**Next Steps:**

- Share your app URL
- Monitor usage
- Gather feedback
- Add features
- Star the repo ⭐

---

**Happy Deploying! 🚀**
