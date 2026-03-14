# Quick Deployment Guide

Deploy your Python Learning Platform in 10 minutes.

## 🚀 Frontend (Vercel)

### 1. Sign up & Connect GitHub
```
1. Go to https://vercel.com
2. Click "Sign Up" → "Continue with GitHub"
3. Authorize and connect your account
```

### 2. Import Project
```
1. Click "New Project"
2. Select "learn-python" repository
3. Click "Import"
```

### 3. Configure Settings
```
Framework: React (auto-detected)
Build Command: cd frontend && npm install && npm run build
Output Directory: frontend/build
```

### 4. Add Environment Variable
```
Name: REACT_APP_API_URL
Value: https://YOUR-BACKEND-URL.com (add later after deploying backend)
```

### 5. Deploy
Click "Deploy" and wait ~3-5 minutes. Your app is live! 🎉

---

## 🛢️ Backend (Render)

### 1. Create Database
```
1. Go to https://render.com (sign up if needed)
2. Click "New +" → "PostgreSQL"
3. Name: python-learning-db
4. Create
5. Copy the database URL
```

### 2. Deploy API
```
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Name: python-learning-api
4. Build Command: pip install -r requirements.txt
5. Start Command: python test_server.py
6. Instance Type: Free
7. Create Web Service
```

### 3. Add Environment Variables
In Service Settings → Environment:
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
FLASK_ENV=production
FLASK_DEBUG=False
JWT_SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

### 4. Deploy
Push to GitHub (Render auto-deploys):
```bash
git push origin main
```

Copy your backend URL from Render (e.g., `https://python-learning-api.onrender.com`)

---

## 🔗 Connect Frontend to Backend

1. Go back to Vercel
2. Project Settings → Environment Variables
3. Update `REACT_APP_API_URL` to your Render backend URL
4. Redeploy by clicking your project and "Redeploy"

---

## ✅ Test Deployment

1. Visit `https://your-project.vercel.app`
2. Register a new account
3. Try the Learn page (run code)
4. Check Dashboard (progress tracking)
5. All working? You're done! 🎉

---

## 📝 Default Test Account
```
Email: test@test.com
Password: 123456
```

---

## 🆘 Troubleshooting

**Frontend won't build:**
- Check build logs on Vercel
- Verify all imports are correct

**Backend returns 500 errors:**
- Check logs on Render dashboard
- Verify DATABASE_URL is correct
- Ensure CORS_ORIGINS is set

**CORS errors:**
- Update CORS_ORIGINS in Render to include Vercel URL
- Redeploy backend

---

## 💰 Cost

- **Vercel**: Free tier (10GB/month)
- **Render**: Free tier (~$7/month for PostgreSQL)
- **Total**: ~$7/month

---

## 🎯 Next Steps (Optional)

- Connect custom domain
- Set up monitoring alerts
- Configure automatic backups
- Add video lessons
- Implement more languages

---

For detailed info, see `DEPLOYMENT.md`
