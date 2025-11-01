# Deploy to Fly.io - Step by Step

## Why Fly.io?
- ✅ Easy CLI deployment
- ✅ Good free tier
- ✅ No web login needed (uses CLI)
- ✅ Fast deployment

## Step 1: Install Fly CLI

```bash
# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Or with Homebrew (macOS)
brew install flyctl

# Verify installation
fly version
```

## Step 2: Login via CLI

```bash
fly auth login
```

This will:
- Open browser for authentication
- Or give you a login URL
- Much easier than web interface!

## Step 3: Initialize App

```bash
cd /Users/ken/Documents/GitHub/fashion_clip
fly launch
```

This will:
- Create `fly.toml` (I've already created it!)
- Ask for app name (or use default)
- Set up deployment

## Step 4: Deploy

```bash
fly deploy
```

First deploy takes 10-15 minutes (model download).

## Step 5: Open Your App

```bash
fly open
```

Or visit: `https://your-app-name.fly.dev`

## Configuration

I've already created `fly.toml` with:
- ✅ Health check endpoint
- ✅ Port configuration
- ✅ HTTP/HTTPS setup

## Environment Variables

Set via CLI:
```bash
fly secrets set SUPABASE_URL=your-url
fly secrets set SUPABASE_KEY=your-key
fly secrets set SUPABASE_SERVICE_KEY=your-service-key
```

## Advantages

✅ **CLI-based** - No web login issues
✅ **Fast deployment** - Usually works first try
✅ **Good free tier** - Generous limits
✅ **Easy scaling** - Simple commands

## Testing

```bash
# Health check
curl https://your-app.fly.dev/health

# API docs
https://your-app.fly.dev/docs
```

Try Fly.io - it's often easier than Railway for CLI-based deployment!

