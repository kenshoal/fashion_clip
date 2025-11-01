# Railway CLI Deployment Guide

## Step 1: Install Railway CLI

### Option A: Using npm (if you have Node.js)
```bash
npm install -g @railway/cli
```

### Option B: Using Homebrew (macOS)
```bash
brew install railway
```

### Option C: Using cURL (direct install)
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Option D: Manual Install
1. Go to https://railway.app/cli
2. Download the binary for your OS
3. Add to PATH

## Step 2: Login to Railway

```bash
railway login
```

This will:
- Open your browser
- Let you authenticate with GitHub/email
- Complete login automatically

**If browser doesn't open:**
```bash
railway login --browserless
```
This gives you a token to paste.

## Step 3: Initialize Project

```bash
cd /Users/ken/Documents/GitHub/fashion_clip
railway init
```

This will:
- Ask for project name (or use default)
- Create `.railway` folder (local config)
- Link to Railway account

## Step 4: Link to Existing Project (Optional)

If you already created a project on Railway website:
```bash
railway link
```
Select your project from the list.

## Step 5: Deploy

### Deploy from current directory:
```bash
railway up
```

This will:
- Build your Docker image
- Deploy to Railway
- Show build logs

### Or deploy specific files:
```bash
railway up --detach
```

## Step 6: Set Environment Variables

```bash
# Set Supabase URL
railway variables set SUPABASE_URL=your-url

# Set Supabase Key
railway variables set SUPABASE_KEY=your-key

# Set Supabase Service Key
railway variables set SUPABASE_SERVICE_KEY=your-service-key

# Set CORS (optional)
railway variables set CORS_ORIGINS=https://your-frontend.com
```

## Step 7: Get Your URL

```bash
railway domain
```

Or check Railway dashboard for your app URL.

## Step 8: Check Status

```bash
railway status
```

Shows deployment status and logs.

## Step 9: View Logs

```bash
railway logs
```

Shows real-time logs from your deployed service.

## Common Commands

```bash
# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# View logs
railway logs

# Set variables
railway variables set KEY=value

# Open in browser
railway open

# Check status
railway status
```

## Troubleshooting

### "railway: command not found"
- Make sure Railway CLI is installed
- Check if it's in your PATH
- Try: `npm install -g @railway/cli`

### Login Issues
```bash
# Try browserless login
railway login --browserless

# Or logout and login again
railway logout
railway login
```

### Build Fails
```bash
# Check logs
railway logs

# Verify Dockerfile exists
ls Dockerfile

# Try redeploy
railway up
```

## Quick Deploy Script

I can create a script that does all this automatically!

## Next Steps

1. Install Railway CLI
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`

Your API will be live on Railway! 🚀

