#!/bin/bash
# Quick Railway Deployment - Run this script

set -e

echo "🚀 Railway Deployment Script"
echo "============================"
echo ""

cd "$(dirname "$0")"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "Installing..."
    npm install -g @railway/cli
fi

echo "✅ Railway CLI found"
echo ""

# Check if logged in
if railway whoami &>/dev/null; then
    echo "✅ Already logged in!"
    RAILWAY_USER=$(railway whoami 2>/dev/null || echo "unknown")
    echo "Logged in as: $RAILWAY_USER"
    echo ""
else
    echo "🔐 Step 1: Please login to Railway"
    echo "This will open your browser..."
    echo ""
    railway login
    echo ""
fi

# Check if project is initialized
if [ -d ".railway" ] || railway status &>/dev/null; then
    echo "✅ Project already initialized"
    echo ""
else
    echo "📦 Step 2: Initializing Railway project..."
    echo "Press Enter to use default project name, or type a name:"
    railway init
    echo ""
fi

# Deploy
echo "🚀 Step 3: Deploying to Railway..."
echo "This will take 10-15 minutes (model download)..."
echo ""
railway up

echo ""
echo "✅ Deployment in progress!"
echo ""
echo "📊 View logs with: railway logs"
echo "🌐 Get URL with: railway domain"
echo "🔍 Check status with: railway status"
echo ""

