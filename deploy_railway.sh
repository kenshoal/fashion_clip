#!/bin/bash
# Railway CLI Deployment Script

echo "🚀 Railway CLI Deployment"
echo "========================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Railway CLI not found. Installing..."
    
    # Check if npm is available
    if command -v npm &> /dev/null; then
        echo "Installing via npm..."
        npm install -g @railway/cli
    elif command -v brew &> /dev/null; then
        echo "Installing via Homebrew..."
        brew install railway
    else
        echo "❌ Please install Railway CLI manually:"
        echo "   npm install -g @railway/cli"
        echo "   OR"
        echo "   brew install railway"
        exit 1
    fi
    
    echo "✅ Railway CLI installed"
    echo ""
fi

echo "🔐 Step 1: Login to Railway"
echo "This will open your browser for authentication..."
railway login

echo ""
echo "📦 Step 2: Initializing Railway project..."
railway init

echo ""
echo "🔧 Step 3: Setting environment variables (optional)..."
echo "Do you want to set Supabase credentials? (y/n)"
read -r SET_VARS

if [ "$SET_VARS" = "y" ]; then
    echo "Enter SUPABASE_URL:"
    read -r SUPABASE_URL
    echo "Enter SUPABASE_KEY:"
    read -r SUPABASE_KEY
    echo "Enter SUPABASE_SERVICE_KEY:"
    read -r SUPABASE_SERVICE_KEY
    
    railway variables set SUPABASE_URL="$SUPABASE_URL"
    railway variables set SUPABASE_KEY="$SUPABASE_KEY"
    railway variables set SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY"
    
    echo "✅ Environment variables set"
fi

echo ""
echo "🚀 Step 4: Deploying to Railway..."
echo "This may take 10-15 minutes (model download)..."
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Getting your URL..."
railway domain

echo ""
echo "📊 View logs:"
echo "   railway logs"
echo ""
echo "🌐 Open in browser:"
echo "   railway open"
