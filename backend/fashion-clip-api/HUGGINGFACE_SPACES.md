# Deploying to Hugging Face Spaces

This guide explains how to deploy the FashionCLIP API to Hugging Face Spaces.

## Quick Setup

1. **Create a new Space** on [Hugging Face Spaces](https://huggingface.co/spaces)

   - Choose **Docker** as the SDK
   - Set visibility to Public or Private as needed

2. **Upload your code** to the Space repository

3. **Set environment variables** in Space Settings → Secrets:

   - `SUPABASE_URL` (optional for demo)
   - `SUPABASE_KEY` (optional for demo)
   - `SUPABASE_SERVICE_KEY` (optional for demo)

   **Note**: For a public demo without Supabase, you can skip these secrets.

4. **Configure CORS** in your `.env` or environment variables:
   - `CORS_ORIGINS=https://your-frontend-url.com`

## File Structure for HF Spaces

```
.
├── app.py                    # Entry point (HF Spaces looks for this)
├── main.py                   # FastAPI application
├── config.py                 # Configuration
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration (optional)
├── models/
│   ├── embedding_model.py
│   └── faiss_manager.py
└── services/
    └── item_service.py
```

## Configuration

### Option 1: Using Environment Variables (Recommended)

Set secrets in Hugging Face Spaces Settings → Secrets:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_KEY`
- `CORS_ORIGINS` (comma-separated URLs)

### Option 2: Standalone Mode (No Supabase)

If you don't set Supabase credentials, the API runs in standalone mode:

- ✅ Can upload items and generate embeddings
- ✅ Can get recommendations from uploaded items
- ❌ Cannot fetch items from Supabase database
- ❌ Outfit recommendations require Supabase

## Dockerfile (Optional)

If you want to customize the Docker image, create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (HF Spaces uses 7860 by default)
EXPOSE 7860

# Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

## Hugging Face Spaces Automatic Configuration

Hugging Face Spaces will:

- Detect `app.py` and use it as the entry point
- Use `requirements.txt` to install dependencies
- Make secrets available as environment variables
- Expose the app on port 7860

## API Endpoints

Once deployed, your API will be available at:

```
https://your-username-spaces.hf.space/api/v1/...
```

Example:

```
https://your-username-spaces.hf.space/api/v1/health
```

## Testing the Deployment

1. **Health Check**:

   ```bash
   curl https://your-username-spaces.hf.space/api/v1/health
   ```

2. **Upload Item** (if Supabase is configured):
   ```bash
   curl -X POST https://your-username-spaces.hf.space/api/v1/items/upload \
     -F "file=@image.jpg" \
     -F "item_id=test-123" \
     -F "user_id=user-456" \
     -F "category=top"
   ```

## Troubleshooting

### Error: "Field required" for Supabase

- This is now fixed! Supabase fields are optional
- The API will run in standalone mode if credentials aren't provided

### Model Download Issues

- First deployment downloads ~1.5GB model
- This may take 5-10 minutes
- Subsequent deployments are faster (model cached)

### Memory Issues

- HF Spaces free tier: 16GB RAM (usually sufficient)
- If OOM errors occur, consider upgrading to a paid tier

### Port Configuration

- HF Spaces uses port 7860 by default
- Make sure your app listens on `0.0.0.0:7860`
- The `app.py` wrapper handles this automatically

## Notes

- **Data Persistence**: FAISS index is stored in `/app/data/`
- HF Spaces provides persistent storage, so the index persists between restarts
- **Scaling**: Free tier has limitations; upgrade for production use
- **CORS**: Make sure to set `CORS_ORIGINS` to allow your frontend

## Example Space Configuration

Check the example Space at: https://huggingface.co/spaces/canken/fashion_clip
