# Deployment Guide

This guide covers deploying the Python Learning Platform to production using Vercel (frontend) and Render (backend).

## Architecture Overview

- **Frontend**: React app deployed on Vercel (static + serverless functions)
- **Backend**: Flask API deployed on Render (or Railway/Heroku alternative)
- **Database**: SQLite (can be migrated to PostgreSQL for better reliability)

## Prerequisites

- GitHub account with your repository pushed
- Vercel account (free): https://vercel.com
- Render account (free): https://render.com
- Environment variables configured

## Part 1: Deploy Frontend to Vercel

### Step 1: Connect GitHub Repository

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "New Project"
3. Select your `learn-python` repository
4. Vercel will auto-detect it's a React app

### Step 2: Configure Build Settings

Vercel should auto-detect:
- **Framework Preset**: React
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/build`
- **Install Command**: `npm install`

### Step 3: Set Environment Variables

In Vercel Project Settings → Environment Variables, add:

```
REACT_APP_API_URL=https://your-backend-url.com
```

Replace `https://your-backend-url.com` with your deployed backend URL (from Step 5 below).

### Step 4: Deploy

Click "Deploy" and wait for the build to complete. Your frontend will be live at `https://your-project-name.vercel.app`

---

## Part 2: Deploy Backend to Render

### Step 1: Create a PostgreSQL Database on Render (Recommended)

1. Go to [render.com](https://render.com) and sign up
2. Create a new PostgreSQL database:
   - Click "New +"
   - Select "PostgreSQL"
   - Name: `python-learning-db`
   - Region: Choose closest to you
   - Create
3. Copy the Internal Database URL - you'll need this

### Step 2: Update Backend for PostgreSQL (Optional but Recommended)

Update `backend/requirements.txt`:
```
psycopg2-binary==2.9.9
```

Update `backend/test_server.py` - change the database connection:
```python
# Before (SQLite):
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test.db'

# After (PostgreSQL):
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/test.db')
```

### Step 3: Create Render Web Service

1. Go to Render dashboard
2. Click "New +"
3. Select "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `python-learning-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python test_server.py`
   - **Instance Type**: Free

### Step 4: Set Environment Variables in Render

In Service Settings → Environment, add:

```
DATABASE_URL=postgresql://user:password@host:5432/python-learning-db
FLASK_ENV=production
FLASK_DEBUG=False
JWT_SECRET_KEY=your-super-secret-key-change-this
CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-domain.com
```

### Step 5: Configure CORS in Backend

Update `backend/test_server.py`:

```python
from flask_cors import CORS
import os

# After creating Flask app:
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})
```

### Step 6: Deploy

Push your changes to GitHub. Render will auto-deploy when it detects changes.

Get your backend URL from Render (e.g., `https://python-learning-api.onrender.com`)

---

## Part 3: Connect Frontend to Backend

After backend is deployed:

1. Go to Vercel dashboard
2. Go to Project Settings → Environment Variables
3. Update `REACT_APP_API_URL` to your backend URL
4. Trigger a redeploy (Vercel will automatically redeploy)

---

## Database Considerations

### Using SQLite (Current)
- ✅ No database setup needed
- ❌ Not reliable for multiple concurrent users
- ❌ Data lost if Render restarts

### Using PostgreSQL (Recommended)
- ✅ Reliable, production-ready
- ✅ Free tier available on Render
- ✅ Automatic backups
- Requires small code changes (see Step 2 above)

---

## Testing After Deployment

1. Visit your Vercel frontend URL
2. Test user registration and login
3. Test code execution in Learn page
4. Check dashboard and progress tracking
5. Verify streak and achievements

---

## Troubleshooting

### Frontend won't build
- Check `npm install` works locally
- Ensure all imports are correct
- Check environment variables are set

### Backend returns 500 errors
- Check Render logs: Dashboard → Service → Logs
- Verify DATABASE_URL is set correctly
- Ensure CORS_ORIGINS includes your Vercel URL

### API calls fail with CORS error
- Update `CORS_ORIGINS` in Render environment
- Include both `https://your-app.vercel.app` and custom domains

### Database connection fails
- Verify PostgreSQL credentials
- Check network access is allowed
- Test locally first: `psql postgresql://user:password@host/db`

---

## Monitoring & Maintenance

### Render
- Monitor logs for errors
- Check CPU/memory usage
- Set up alerts for failures

### Vercel
- Check build logs
- Monitor function execution time
- Review error tracking

---

## Optional Enhancements

1. **Custom Domain**: Connect both Vercel and Render to your domain
2. **SSL Certificate**: Automatically included with Vercel and Render
3. **Analytics**: Enable Vercel Analytics for frontend insights
4. **Database Backups**: Configure auto-backups on Render PostgreSQL
5. **CDN**: Vercel includes CDN by default

---

## Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Enable HTTPS (automatic with Vercel/Render)
- [ ] Restrict CORS to only your frontend domain
- [ ] Use environment variables for all secrets
- [ ] Enable rate limiting on API endpoints

---

## Cost Summary

- **Vercel Frontend**: Free tier (10 GB bandwidth/month)
- **Render Backend**: Free tier ($7/month PostgreSQL recommended)
- **Total**: ~$7/month for production-ready deployment

---

For issues or questions, check:
- [Vercel Docs](https://vercel.com/docs)
- [Render Docs](https://render.com/docs)
- Flask documentation
- React documentation
