# Todo App - Complete Deployment Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Production Deployment](#production-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- Git installed

### Step 1: Clone and Setup (If Not Already Done)

```bash
cd /mnt/c/Users/DELL/Desktop/Projects/PROJECT\ 2/PHASE_2
```

### Step 2: Backend Setup (Local)

```bash
# Navigate to backend
cd backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
# On Windows WSL/Linux:
source venv/bin/activate
# On Windows CMD:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (if not exists)
cat > .env << EOF
DATABASE_URL=sqlite:///./test.db
BETTER_AUTH_SECRET=test-secret-key-with-at-least-32-characters-for-jwt-signing
EOF

# Initialize database
python init_db.py

# Start backend server
uvicorn src.main:app --reload
```

**Backend will run at:** http://localhost:8000

### Step 3: Frontend Setup (Local)

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file (if not exists)
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start frontend server
npm run dev
```

**Frontend will run at:** http://localhost:3000

### Step 4: Test Locally

1. Open browser: http://localhost:3000
2. Click "Get Started" to sign up
3. Create an account
4. Start adding tasks!

---

## Production Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│  Frontend (Vercel)                          │
│  - Next.js static site                      │
│  - URL: https://your-app.vercel.app        │
└─────────────────────────────────────────────┘
                    ↓ API Calls
┌─────────────────────────────────────────────┐
│  Backend (Railway/Render)                   │
│  - FastAPI server                           │
│  - URL: https://your-api.railway.app       │
└─────────────────────────────────────────────┘
                    ↓ Database Queries
┌─────────────────────────────────────────────┐
│  Database (Neon PostgreSQL)                 │
│  - Serverless PostgreSQL                    │
│  - Connection string from Neon              │
└─────────────────────────────────────────────┘
```

---

## Option 1: Quick Deployment (Recommended)

### A. Database Setup - Neon PostgreSQL (FREE)

1. **Create Neon Account:**
   - Go to: https://neon.tech
   - Sign up (free tier)
   - Click "Create Project"

2. **Get Connection String:**
   - Project name: `todo-app-db`
   - Region: Choose closest to you
   - After creation, copy the connection string
   - Format: `postgresql://user:password@host/database?sslmode=require`

3. **Save Connection String** (you'll need this later)

---

### B. Backend Deployment - Railway (FREE)

1. **Create Railway Account:**
   - Go to: https://railway.app
   - Sign up with GitHub
   - Connect your GitHub account

2. **Deploy Backend:**
   ```bash
   # In your backend directory, create railway.json
   cd backend
   ```

   Create `railway.json`:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

   Create `Procfile`:
   ```
   web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Push to GitHub:**
   ```bash
   # Initialize git if not already
   cd /mnt/c/Users/DELL/Desktop/Projects/PROJECT\ 2/PHASE_2
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

4. **Deploy on Railway:**
   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Choose `/backend` as root directory
   - Add environment variables:
     - `DATABASE_URL`: (Neon connection string)
     - `BETTER_AUTH_SECRET`: (generate strong 64-char random string)

5. **Generate Secret Key:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

6. **Copy Backend URL:**
   - After deployment, Railway will give you a URL
   - Example: `https://todo-backend-production.up.railway.app`

---

### C. Frontend Deployment - Vercel (FREE)

1. **Create Vercel Account:**
   - Go to: https://vercel.com
   - Sign up with GitHub

2. **Prepare Frontend:**
   ```bash
   cd frontend

   # Update .env.local for production
   # Create .env.production
   cat > .env.production << EOF
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   EOF
   ```

3. **Deploy to Vercel:**
   - Go to Vercel dashboard
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Root directory: `frontend`
   - Framework Preset: Next.js
   - Environment Variables:
     - `NEXT_PUBLIC_API_URL`: (your Railway backend URL)
   - Click "Deploy"

4. **Your App is Live!**
   - Vercel will give you a URL: `https://your-app.vercel.app`

---

## Option 2: Alternative Free Hosting

### Backend: Render.com (Alternative to Railway)

1. Go to: https://render.com
2. Sign up with GitHub
3. Create "New Web Service"
4. Connect repository
5. Settings:
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - Environment variables:
     - `DATABASE_URL`: (Neon connection string)
     - `BETTER_AUTH_SECRET`: (64-char random string)

### Frontend: Netlify (Alternative to Vercel)

1. Go to: https://netlify.com
2. Sign up with GitHub
3. Import project
4. Build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `.next`
5. Environment variable:
   - `NEXT_PUBLIC_API_URL`: (backend URL)

---

## Environment Configuration

### Development (.env)
```bash
# Backend - backend/.env
DATABASE_URL=sqlite:///./test.db
BETTER_AUTH_SECRET=test-secret-key-with-at-least-32-characters

# Frontend - frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (.env)
```bash
# Backend - Set in Railway/Render dashboard
DATABASE_URL=postgresql://user:pass@neon-host/db?sslmode=require
BETTER_AUTH_SECRET=<64-char-random-string>

# Frontend - Set in Vercel/Netlify dashboard
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Database Migration (Neon Setup)

Once you have Neon PostgreSQL connection string:

```bash
# Update backend/.env with Neon URL
cd backend
source venv/bin/activate

# Update .env
echo "DATABASE_URL=postgresql://your-neon-connection-string" > .env
echo "BETTER_AUTH_SECRET=your-secret-key" >> .env

# Run migrations
python init_db.py

# Test connection
python -c "from src.database import engine; print('Database connected!')"
```

---

## Post-Deployment Checklist

### Backend Verification
- [ ] Backend URL accessible: `https://your-backend.railway.app`
- [ ] Health check works: `curl https://your-backend.railway.app/`
- [ ] API docs accessible: `https://your-backend.railway.app/docs`
- [ ] Database connected (check logs)
- [ ] Environment variables set correctly

### Frontend Verification
- [ ] Frontend URL accessible: `https://your-app.vercel.app`
- [ ] Can see landing page
- [ ] Signup works
- [ ] Login works
- [ ] Dashboard loads
- [ ] Can create/edit/delete tasks

### Security Check
- [ ] HTTPS enabled on both frontend and backend
- [ ] BETTER_AUTH_SECRET is strong (64+ characters)
- [ ] Database connection uses SSL (`?sslmode=require`)
- [ ] No secrets in code (all in environment variables)
- [ ] CORS configured for production domain

---

## CORS Configuration for Production

Update `backend/src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# Update origins for production
origins = [
    "http://localhost:3000",  # Local development
    "https://your-app.vercel.app",  # Production frontend
    # Add your custom domain if you have one
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Update this list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Cost Breakdown (FREE Tier)

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Neon PostgreSQL** | ✅ FREE | 0.5 GB storage, 1 project |
| **Railway** | ✅ FREE | $5 credit/month (enough for small apps) |
| **Vercel** | ✅ FREE | 100 GB bandwidth, unlimited projects |
| **Render** | ✅ FREE | 750 hours/month |
| **Netlify** | ✅ FREE | 100 GB bandwidth |

**Total Cost: $0/month** for hobby/personal projects!

---

## Custom Domain (Optional)

### Add Custom Domain to Vercel
1. Buy domain (Namecheap, GoDaddy, etc.)
2. Go to Vercel project settings
3. Add domain
4. Update DNS records (Vercel provides instructions)

### Add Custom Domain to Railway
1. Go to Railway project settings
2. Add custom domain
3. Update DNS records

---

## Monitoring & Logs

### Railway Logs
- Go to Railway dashboard
- Click on your service
- View "Logs" tab for real-time logs

### Vercel Logs
- Go to Vercel dashboard
- Click on deployment
- View "Functions" tab for server logs

### Neon Database
- Go to Neon dashboard
- Monitor queries and performance
- View connection stats

---

## Troubleshooting

### Backend Not Starting
```bash
# Check logs in Railway/Render
# Common issues:
- Database connection string incorrect
- BETTER_AUTH_SECRET not set
- Port not set (Railway uses $PORT)
```

### Frontend Can't Connect to Backend
```bash
# Check:
- NEXT_PUBLIC_API_URL is correct
- CORS is configured
- Backend is running
- HTTPS/HTTP mismatch
```

### Database Connection Failed
```bash
# Verify:
- Connection string format correct
- SSL mode required for Neon
- Database exists
- User has correct permissions
```

### 401 Unauthorized Errors
```bash
# Check:
- BETTER_AUTH_SECRET matches on both backend and frontend
- JWT token is being sent correctly
- Token not expired
```

---

## Quick Commands Reference

### Local Development
```bash
# Backend
cd backend && source venv/bin/activate && uvicorn src.main:app --reload

# Frontend (new terminal)
cd frontend && npm run dev
```

### Production Deploy
```bash
# Push changes
git add .
git commit -m "Update application"
git push origin main

# Railway and Vercel will auto-deploy!
```

### Database Reset
```bash
# Local SQLite
cd backend && rm test.db && python init_db.py

# Neon PostgreSQL
# Use Neon dashboard to reset database
```

---

## Support Resources

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Neon Docs:** https://neon.tech/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Next.js Docs:** https://nextjs.org/docs

---

## Summary

### Local Development ✅
1. Backend: `cd backend && source venv/bin/activate && uvicorn src.main:app --reload`
2. Frontend: `cd frontend && npm run dev`
3. Access: http://localhost:3000

### Production Deployment 🚀
1. Database: Neon PostgreSQL (free)
2. Backend: Railway/Render (free)
3. Frontend: Vercel/Netlify (free)
4. Access: https://your-app.vercel.app

**Total Time:** 30-60 minutes
**Total Cost:** $0/month

---

**You now have a production-ready Todo app running both locally and on the web!** 🎉
