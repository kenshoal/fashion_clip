# FashionCLIP Outfit Recommendation API - Complete Implementation Guide

## 📋 What This Repository Does

This is a **FastAPI microservice** that provides AI-powered outfit recommendations using FashionCLIP embeddings and FAISS vector search. It:

1. **Generates FashionCLIP embeddings** from clothing item images
2. **Stores embeddings in FAISS** for fast similarity search
3. **Recommends compatible items** based on style similarity
4. **Integrates with Supabase** to sync with your existing database
5. **Provides REST API endpoints** for upload, search, and recommendations

### Key Features

- ✅ Upload clothing item images and generate embeddings
- ✅ Store embeddings in FAISS index (fast vector search)
- ✅ Store metadata in PostgreSQL/Supabase
- ✅ Recommend compatible items using cosine similarity
- ✅ Category-aware recommendations (shirts → pants, shoes, etc.)
- ✅ Complete outfit recommendations based on multiple items
- ✅ Scalable architecture with vector search

## 🏗️ Architecture

```
Vue.js Frontend
    ↓ HTTP/JSON
FastAPI Backend
    ├── FashionCLIP Model (generates 512-dim embeddings)
    ├── FAISS Index (stores embeddings for fast search)
    └── Supabase (stores item metadata)
```

## 🚀 How to Implement It Now

### Step 1: Install Dependencies

```bash
cd backend/fashion-clip-api
pip install -r requirements.txt
```

**Note**: First installation will download the FashionCLIP model (~1.5GB), which may take a few minutes.

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp env.example.txt .env

# Edit .env and add your Supabase credentials:
```

**Required variables in `.env`:**

```env
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True

# CORS (add your frontend URL)
CORS_ORIGINS=http://localhost:5173,https://your-domain.com
```

**How to get Supabase credentials:**

1. Go to your Supabase project dashboard
2. Settings → API
3. Copy:
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_KEY`
   - service_role key → `SUPABASE_SERVICE_KEY`

### Step 3: (Optional) Initialize FAISS Index with Existing Items

If you already have clothing items in Supabase, migrate them to the FAISS index:

```bash
python scripts/init_faiss_index.py
```

This will:

- Fetch all items from your `clothes` table
- Download images and generate embeddings
- Add them to the FAISS index

### Step 4: Run the Server

**Development mode:**

```bash
uvicorn main:app --reload --port 8000
```

**Production mode:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Step 4: Test the API

**Health check:**

```bash
curl http://localhost:8000/api/v1/health
```

**Upload an item:**

```bash
curl -X POST http://localhost:8000/api/v1/items/upload \
  -F "file=@path/to/image.jpg" \
  -F "item_id=test-123" \
  -F "user_id=user-456" \
  -F "category=top"
```

**Get recommendations:**

```bash
curl -X POST http://localhost:8000/api/v1/items/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "test-123",
    "user_id": "user-456",
    "k": 5,
    "target_categories": ["bottom", "shoes"]
  }'
```

## 📡 API Endpoints

### 1. Health Check

```
GET /api/v1/health
```

Returns service status and statistics.

### 2. Upload Item

```
POST /api/v1/items/upload
Content-Type: multipart/form-data

Fields:
- file: Image file (required)
- item_id: Item ID from Supabase (required)
- user_id: User ID (required)
- category: Item category: top, bottom, shoes, dress, outerwear (required)
- image_url: URL where image is stored (optional)
- name: Item name (optional)
```

### 3. Get Item Recommendations

```
POST /api/v1/items/recommendations
Content-Type: application/json

Body:
{
  "item_id": "uuid-123",
  "user_id": "user-456",
  "k": 10,                          // Number of recommendations
  "target_categories": ["bottom"],  // Optional: filter by categories
  "min_similarity": 0.5            // Optional: minimum similarity score
}
```

### 4. Get Outfit Recommendations

```
POST /api/v1/outfits/recommend
Content-Type: application/json

Body:
{
  "base_items": ["item-1", "item-2"],  // List of item IDs
  "user_id": "user-456",
  "k_per_category": 3                  // Recommendations per category
}
```

### 5. Remove Item

```
DELETE /api/v1/items/{item_id}
```

Removes item from FAISS index.

### 6. Get Statistics

```
GET /api/v1/stats
```

Returns service statistics (total items, categories, etc.).

## 🔧 Integration with Vue.js Frontend

See `integration_guide.md` for detailed Vue.js integration examples.

**Quick example:**

```javascript
// Upload item after creating it in Supabase
const formData = new FormData();
formData.append("file", imageFile);
formData.append("item_id", supabaseItemId);
formData.append("user_id", userId);
formData.append("category", "top");

await fetch("http://localhost:8000/api/v1/items/upload", {
  method: "POST",
  body: formData,
});

// Get recommendations
const response = await fetch(
  "http://localhost:8000/api/v1/items/recommendations",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      item_id: itemId,
      user_id: userId,
      k: 5,
    }),
  }
);
const { recommendations } = await response.json();
```

## 🗄️ Database Setup (Optional)

If you want to store embedding backups in Supabase:

1. Run the migration SQL (optional, for backup embeddings):

```sql
-- In Supabase SQL editor
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE clothes
ADD COLUMN IF NOT EXISTS embedding vector(512),
ADD COLUMN IF NOT EXISTS faiss_id INTEGER;

CREATE INDEX IF NOT EXISTS clothes_embedding_idx
ON clothes USING ivfflat (embedding vector_cosine_ops);
```

**Note**: FAISS is the primary storage. Supabase embedding storage is optional.

## 📦 File Structure

```
backend/fashion-clip-api/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from env.example.txt)
│
├── models/
│   ├── embedding_model.py # FashionCLIP model wrapper
│   └── faiss_manager.py   # FAISS index manager
│
├── services/
│   └── item_service.py    # Business logic
│
├── database/
│   └── migration.sql      # Optional DB migrations
│
└── scripts/
    └── init_faiss_index.py  # Migration tool for existing items
```

## 🐛 Troubleshooting

### Model Download Issues

- First run downloads ~1.5GB model from HuggingFace
- Ensure stable internet connection
- Model cached in `~/.cache/huggingface/`

### FAISS Issues

- Index stored in `./data/faiss_index.bin`
- Ensure write permissions on `./data/` directory
- Delete index file to rebuild from scratch

### Memory Issues

- FashionCLIP requires ~2GB RAM
- Use GPU if available: set `DEVICE=cuda` in `.env`
- Reduce batch size if OOM errors

### CORS Errors

- Update `CORS_ORIGINS` in `.env` with your frontend URL
- Restart server after changes

### Import Errors

- Ensure you're in the `backend/fashion-clip-api/` directory
- Install all dependencies: `pip install -r requirements.txt`

## 🚢 Deployment

### Railway/Render/Fly.io

1. **Set environment variables** in your hosting platform
2. **Ensure persistent storage** for `./data/` directory (for FAISS index)
3. **Configure CORS** with your production frontend URL
4. **Use GPU** if available (set `DEVICE=cuda`)

**Example for Railway:**

- Add all `.env` variables as Railway secrets
- Mount persistent volume at `/app/data`
- Deploy from Git repository

## 📊 Performance Notes

- **Embedding generation**: ~100-200ms per image (CPU), ~20-50ms (GPU)
- **FAISS search**: <10ms for thousands of items
- **API response time**: Target <500ms end-to-end

## 🎯 Next Steps

1. ✅ Set up environment variables
2. ✅ Run the server
3. ✅ Test with sample uploads
4. ✅ Integrate with Vue.js frontend
5. ✅ Deploy to production
6. ✅ Monitor performance

## 📚 Additional Resources

- [FashionCLIP Paper](https://arxiv.org/abs/2203.00791)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)

---

**Status**: ✅ All core files are implemented and ready to use!
