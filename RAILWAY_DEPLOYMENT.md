# Deploy to Railway - Complete Guide

## 🚀 Quick Start

Railway is the easiest platform for deploying FastAPI apps with ML models!

## Step 1: Create Railway Account

1. Go to **https://railway.app**
2. Click **"Login"** → **"Start a New Project"**
3. Sign in with **GitHub** (recommended) or email
4. Railway gives you **$5 free credit/month** - perfect for your API!

## Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: **`fashion_clip`** (or `kenshoal/fashion_clip`)
4. Click **"Deploy Now"**

## Step 3: Configure Service (Usually Auto-Detected!)

Railway is smart - it will usually:
- ✅ Auto-detect your `Dockerfile`
- ✅ Set up build automatically
- ✅ Configure start command

**But verify these settings:**

1. Click on your service → **Settings** tab
2. **Build Command**: (leave empty - uses Dockerfile)
3. **Start Command**: 
   ```
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
   (Railway sets `$PORT` automatically)

## Step 4: Environment Variables

Click **"Variables"** tab and add:

### Required:
- (None - PORT is set automatically by Railway)

### Optional (for Supabase):
- `SUPABASE_URL` = Your Supabase project URL
- `SUPABASE_KEY` = Your Supabase anon key
- `SUPABASE_SERVICE_KEY` = Your Supabase service key

### Optional (CORS):
- `CORS_ORIGINS` = `https://your-frontend-url.com,http://localhost:5173`

### Optional (Model/Performance):
- `DEVICE` = `cpu` (or `cuda` if you upgrade to GPU)
- `LOG_LEVEL` = `INFO`

## Step 5: Deploy!

1. Railway will automatically:
   - Build your Docker image
   - Install dependencies
   - Start your service

2. **First build takes 10-15 minutes** (model download)

3. Watch the build logs in real-time

## Step 6: Get Your URL

Once deployed:
1. Click **"Settings"** → **"Networking"**
2. Click **"Generate Domain"** (creates a public URL)
3. Your API will be at: `https://your-app-name.up.railway.app`

## 🧪 Testing After Deployment

Test your API:

```bash
# Health check
curl https://your-app.up.railway.app/health

# Stats
curl https://your-app.up.railway.app/stats

# Root
curl https://your-app.up.railway.app/

# API Documentation
https://your-app.up.railway.app/docs
```

## 💰 Pricing

**Free Tier:**
- $5 credit/month (usually enough for small APIs)
- No fixed memory limits
- Auto-scales based on usage
- Perfect for development/testing

**Paid Plans:**
- Developer: $5/month (more credits)
- Team: $20/month per user
- Enterprise: Custom

## ✅ What's Configured

- ✅ `railway.json` - Railway configuration
- ✅ `Dockerfile` - Works with Railway
- ✅ Port binding - Uses `$PORT` env var
- ✅ All endpoints ready

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Railway dashboard
- Verify `Dockerfile` is in root directory
- Ensure all files are committed to GitHub

### Service Won't Start
- Check service logs
- Verify PORT env var is being used
- Ensure `app.py` imports correctly

### Out of Memory
- Railway free tier should handle FashionCLIP
- If issues, upgrade to paid plan
- Or optimize model loading (lazy load)

### Port Issues
- Railway sets `$PORT` automatically
- Your Dockerfile uses `${PORT:-7860}` - this is correct
- No need to set PORT manually

## 🎯 Advantages of Railway

✅ **Better for ML models** - More flexible memory limits
✅ **Auto-detection** - Finds Dockerfile automatically  
✅ **Easy deployment** - Just connect GitHub
✅ **Real-time logs** - See what's happening
✅ **Free tier friendly** - $5/month credit
✅ **No routing issues** - Unlike HF Spaces!

## 📝 Next Steps

1. ✅ Connect GitHub repo to Railway
2. ✅ Add environment variables (optional)
3. ✅ Wait for first build
4. ✅ Test endpoints
5. ✅ Update frontend with new URL

## 🚀 Quick Deploy Command (Alternative)

If you have Railway CLI installed:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up
```

But the GitHub method is easier!

---

**Your API should work perfectly on Railway!** The free tier is much better for ML models than Render. 🎉

