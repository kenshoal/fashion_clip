# Quick Start Guide

## 1. Installation

```bash
cd backend/fashion-clip-api
pip install -r requirements.txt
```

## 2. Configuration

```bash
# Copy environment template
cp env.example.txt .env

# Edit .env with your settings
# - Add Supabase credentials
# - Configure CORS origins
```

## 3. Initialize FAISS Index (Optional)

If you have existing items in Supabase, migrate them:

```bash
python scripts/init_faiss_index.py
```

## 4. Run the Server

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 5. Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload an item (example)
curl -X POST http://localhost:8000/api/v1/items/upload \
  -F "file=@image.jpg" \
  -F "item_id=test-123" \
  -F "user_id=user-456" \
  -F "category=top"

# Get recommendations
curl -X POST http://localhost:8000/api/v1/items/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "test-123",
    "user_id": "user-456",
    "k": 5,
    "target_categories": ["bottom", "shoes"]
  }'
```

## 6. Integration

See `integration_guide.md` for Vue.js frontend integration.

## Troubleshooting

### Model Download Issues
- First run downloads ~1.5GB model
- Ensure stable internet connection
- Model cached in `~/.cache/huggingface/`

### FAISS Issues
- Index stored in `./data/faiss_index.bin`
- Ensure write permissions
- Delete index to rebuild from scratch

### Memory Issues
- FashionCLIP requires ~2GB RAM
- Use GPU if available (set `DEVICE=cuda` in .env)
- Reduce batch size if OOM errors

### CORS Errors
- Update `CORS_ORIGINS` in .env
- Restart server after changes

## Next Steps

1. Deploy backend to Railway/Render/Fly.io
2. Update frontend environment variables
3. Integrate with Vue.js app (see integration guide)
4. Monitor performance and optimize

