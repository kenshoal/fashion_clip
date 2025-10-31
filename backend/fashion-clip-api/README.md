# FashionCLIP Outfit Recommendation API

A FastAPI microservice that provides AI-powered outfit recommendations using FashionCLIP embeddings and FAISS vector search.

## Architecture Overview

```
┌─────────────────┐
│   Vue.js App    │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/JSON
         │
┌────────▼──────────────────────────┐
│   FastAPI Backend Service        │
│   - Image Upload Handling        │
│   - FashionCLIP Embedding        │
│   - FAISS Vector Search          │
│   - Recommendation Logic         │
└────────┬─────────────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐  ┌──▼─────┐
│ FAISS │  │PostgreSQL│
│Index  │  │(Supabase)│
└───────┘  └─────────┘
```

## Features

- ✅ Upload images and generate FashionCLIP embeddings
- ✅ Store embeddings in FAISS index for fast similarity search
- ✅ Store metadata in PostgreSQL (via Supabase)
- ✅ Recommend compatible items using cosine similarity
- ✅ Category-aware recommendations (shirts → pants, shoes, etc.)
- ✅ Scalable architecture with vector search
- ✅ RESTful API endpoints
- ✅ Image processing and validation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Initialize FAISS index:
```bash
python scripts/init_faiss_index.py
```

4. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `POST /api/v1/items/upload` - Upload item and generate embedding
- `GET /api/v1/items/{item_id}/recommendations` - Get recommendations for an item
- `POST /api/v1/outfits/recommend` - Get complete outfit recommendations
- `GET /api/v1/health` - Health check
- `DELETE /api/v1/items/{item_id}` - Remove item from index

## Integration with Existing Backend

This service integrates with your Supabase backend:
- Reads/writes item metadata to Supabase PostgreSQL
- Uses Supabase user authentication tokens
- Stores embeddings separately in FAISS for performance

