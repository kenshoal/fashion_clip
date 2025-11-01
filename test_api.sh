#!/bin/bash
# Test script for FashionCLIP API on HF Spaces

BASE_URL="https://canken-spaces.hf.space"

echo "🧪 Testing FashionCLIP API on HF Spaces"
echo "========================================"
echo ""

# Test 1: Root endpoint
echo "1️⃣  Testing root endpoint (/)..."
ROOT_RESPONSE=$(curl -s "$BASE_URL/" 2>&1)
if echo "$ROOT_RESPONSE" | grep -q "FashionCLIP"; then
    echo "✅ Root endpoint working"
    echo "$ROOT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ROOT_RESPONSE"
else
    echo "❌ Root endpoint failed"
    echo "$ROOT_RESPONSE" | head -5
fi
echo ""

# Test 2: Health check
echo "2️⃣  Testing health endpoint (/api/v1/health)..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/v1/health" 2>&1)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health endpoint working"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ Health endpoint failed"
    echo "$HEALTH_RESPONSE" | head -5
fi
echo ""

# Test 3: Stats endpoint
echo "3️⃣  Testing stats endpoint (/api/v1/stats)..."
STATS_RESPONSE=$(curl -s "$BASE_URL/api/v1/stats" 2>&1)
if echo "$STATS_RESPONSE" | grep -q "faiss_stats"; then
    echo "✅ Stats endpoint working"
    echo "$STATS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATS_RESPONSE"
else
    echo "❌ Stats endpoint failed"
    echo "$STATS_RESPONSE" | head -5
fi
echo ""

# Test 4: API Documentation
echo "4️⃣  Testing API docs (/docs)..."
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$DOCS_STATUS" = "200" ]; then
    echo "✅ API docs available at: $BASE_URL/docs"
else
    echo "❌ API docs not accessible (HTTP $DOCS_STATUS)"
fi
echo ""

# Test 5: Recommendations endpoint (should fail gracefully without items)
echo "5️⃣  Testing recommendations endpoint (expected to fail without items)..."
REC_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/items/recommendations" \
    -H "Content-Type: application/json" \
    -d '{"item_id": "test-123", "user_id": "test-user", "k": 5}' 2>&1)
echo "Response:"
echo "$REC_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REC_RESPONSE" | head -10
echo ""

echo "========================================"
echo "✅ Testing complete!"
echo ""
echo "📖 API Documentation: $BASE_URL/docs"
echo "🏥 Health Check: $BASE_URL/api/v1/health"

