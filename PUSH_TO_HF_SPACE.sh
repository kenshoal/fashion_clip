#!/bin/bash
# Script to push to Hugging Face Space

echo "🚀 Pushing to Hugging Face Space..."

# Check if logged in
if ! hf auth whoami &>/dev/null; then
    echo "❌ Not logged in to Hugging Face"
    echo ""
    echo "Please login first:"
    echo "  hf auth login"
    echo ""
    echo "Or if you prefer the old CLI:"
    echo "  huggingface-cli login"
    echo ""
    echo "You'll need a token from: https://huggingface.co/settings/tokens"
    exit 1
fi

echo "✅ Logged in to Hugging Face"

# Push to HF Space
echo ""
echo "📤 Pushing to https://huggingface.co/spaces/canken/fashion_clip..."
git push hf main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to HF Space!"
    echo "📊 Check build status at: https://huggingface.co/spaces/canken/fashion_clip"
else
    echo ""
    echo "❌ Push failed. Check the error above."
    exit 1
fi


