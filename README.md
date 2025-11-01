---
title: FashionCLIP Outfit Recommendation API
emoji: 👗
colorFrom: pink
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# FashionCLIP Outfit Recommendation API

AI-powered outfit recommendations using FashionCLIP embeddings and FAISS vector search.

## Features

- 🎨 Generate FashionCLIP embeddings from clothing images
- 🔍 Fast similarity search with FAISS
- 💡 Style-compatible outfit recommendations
- 🚀 RESTful API endpoints

## Quick Start

The application files are in `backend/fashion-clip-api/`. See the [deployment guide](backend/fashion-clip-api/HUGGINGFACE_SPACES.md) for details.

## API Endpoints

### Health Check

```
GET /api/v1/health
```

### Upload Item

```
POST /api/v1/items/upload
Content-Type: multipart/form-data

Fields:
- file: Image file
- item_id: Item ID
- user_id: User ID
- category: top, bottom, shoes, dress, outerwear
```

### Get Recommendations

```
POST /api/v1/items/recommendations
Content-Type: application/json

{
  "item_id": "item-123",
  "user_id": "user-456",
  "k": 10,
  "target_categories": ["bottom", "shoes"]
}
```

## Configuration

Set these environment variables in Space Settings → Secrets (optional):

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `SUPABASE_SERVICE_KEY` - Your Supabase service key

**Note**: The API works in standalone mode without Supabase (limited functionality).

## Documentation

See `backend/fashion-clip-api/HUGGINGFACE_SPACES.md` for detailed deployment instructions.

