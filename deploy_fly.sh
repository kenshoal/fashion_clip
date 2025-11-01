#!/bin/bash
# Fly.io Deployment Script

echo "🚀 Setting up Fly.io deployment..."
echo ""

# Check if fly CLI is installed
if ! command -v flyctl &> /dev/null && ! command -v fly &> /dev/null; then
    echo "📦 Installing Fly CLI..."
    
    # Install Fly CLI
    curl -L https://fly.io/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.fly/bin:$PATH"
    
    echo "✅ Fly CLI installed"
    echo ""
fi

# Use flyctl or fly (both work)
FLY_CMD=$(command -v flyctl || command -v fly || echo "flyctl")

echo "🔐 Step 1: Login to Fly.io"
echo "This will open your browser for authentication..."
$FLY_CMD auth login

echo ""
echo "📦 Step 2: Creating/initializing app..."
cd "$(dirname "$0")"
$FLY_CMD launch --no-deploy

echo ""
echo "🔧 Step 3: Setting up environment variables (optional)..."
echo "Add your Supabase credentials? (y/n)"
read -r ADD_VARS

if [ "$ADD_VARS" = "y" ]; then
    echo "Enter SUPABASE_URL:"
    read -r SUPABASE_URL
    echo "Enter SUPABASE_KEY:"
    read -r SUPABASE_KEY
    echo "Enter SUPABASE_SERVICE_KEY:"
    read -r SUPABASE_SERVICE_KEY
    
    $FLY_CMD secrets set SUPABASE_URL="$SUPABASE_URL"
    $FLY_CMD secrets set SUPABASE_KEY="$SUPABASE_KEY"
    $FLY_CMD secrets set SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY"
fi

echo ""
echo "🚀 Step 4: Deploying..."
$FLY_CMD deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Opening your app..."
$FLY_CMD open

echo ""
echo "📋 Your API is live!"
echo "Test endpoints:"
echo "  - Health: https://your-app.fly.dev/health"
echo "  - Docs: https://your-app.fly.dev/docs"

