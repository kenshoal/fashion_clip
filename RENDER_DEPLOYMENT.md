# Deploy to Render - Step by Step Guide

## ✅ Files Ready

I've created the necessary files:
- `render.yaml` - Render configuration
- Updated `Dockerfile` - Works with Render's PORT env var

## 🚀 Deployment Steps

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up (free account works)
3. Connect your GitHub account

### Step 2: Create New Web Service

1. **Click "New +"** → **"Web Service"**

2. **Connect Repository:**
   - Select your GitHub account
   - Choose repository: `fashion_clip`
   - Click "Connect"

3. **Configure Service:**
   - **Name**: `fashion-clip-api` (or any name you prefer)
   - **Environment**: `Docker`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `./` if needed)
   - **Dockerfile Path**: `Dockerfile` (should auto-detect)
   - **Docker Context**: `.` (current directory)

4. **Build & Deploy:**
   - **Build Command**: (leave empty - Render uses Dockerfile)
   - **Start Command**: 
     ```
     uvicorn app:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: `Free` (or choose paid if needed)

### Step 3: Environment Variables

Click "Environment" tab and add:

**Required:**
- `PORT` = `7860` (Render sets this automatically, but you can specify)
- `HOST` = `0.0.0.0`

**Optional (for Supabase integration):**
- `SUPABASE_URL` = Your Supabase URL
- `SUPABASE_KEY` = Your Supabase anon key  
- `SUPABASE_SERVICE_KEY` = Your Supabase service key

**Optional (CORS):**
- `CORS_ORIGINS` = `https://your-frontend-url.com,http://localhost:5173`

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Build your Docker image
   - Install dependencies
   - Start your service
3. Wait 5-10 minutes for first build (model download)

### Step 5: Get Your URL

Once deployed, Render will give you a URL like:
```
https://fashion-clip-api.onrender.com
```

## 📋 Quick Setup Checklist

- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Create Web Service (Docker)
- [ ] Set environment variables
- [ ] Deploy
- [ ] Test endpoints

## 🧪 Testing After Deployment

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-app.onrender.com/health

# Stats
curl https://your-app.onrender.com/stats

# Root
curl https://your-app.onrender.com/

# API Docs
https://your-app.onrender.com/docs
```

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify Dockerfile is in root directory
- Ensure all required files are committed to GitHub

### App Won't Start
- Check service logs
- Verify PORT env var is set
- Ensure app.py is in root directory

### 404 Errors
- Verify the service is "Live" (not paused)
- Check that PORT matches in start command
- Review service logs for errors

## 💡 Tips

1. **Free Tier Limits:**
   - Services spin down after 15 min inactivity
   - First request after spin-down takes ~30 seconds
   - Upgrade to paid for always-on

2. **Persistent Storage:**
   - FAISS index is stored in `/app/data/`
   - Render's free tier doesn't persist storage between restarts
   - Consider using external storage (S3, Supabase Storage) for production

3. **Custom Domain:**
   - Render allows custom domains
   - Configure in Settings → Custom Domain

## ✅ What's Configured

- ✅ Dockerfile updated for Render
- ✅ render.yaml created (optional, for declarative config)
- ✅ Port configuration ready
- ✅ All endpoints working
- ✅ Health check endpoint configured

## 🎯 Next Steps

1. Follow the deployment steps above
2. Test your API endpoints
3. Update your frontend to use the new Render URL
4. (Optional) Set up custom domain

Your API should work perfectly on Render! 🚀

