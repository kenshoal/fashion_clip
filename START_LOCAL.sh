#!/bin/bash
# Start API locally - No deployment needed!

echo "🚀 Starting FashionCLIP API locally..."
echo ""

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo ""
echo "✅ Starting server on http://localhost:8000"
echo "📖 API docs at: http://localhost:8000/docs"
echo ""
echo "In another terminal, run: ngrok http 8000"
echo "This will give you a public URL!"
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000

