# Hugging Face Spaces Deployment - Fixed Issues

## Problem

The API was failing to start on Hugging Face Spaces with this error:

```
pydantic_core._pydantic_core.ValidationError: 3 validation errors for Settings
supabase_url Field required
supabase_key Field required
supabase_service_key Field required
```

## Solution

### ✅ Changes Made

1. **Made Supabase fields optional** in `config.py`

   - Changed from required fields to optional with empty string defaults
   - API can now run in "standalone mode" without Supabase

2. **Updated `ItemService`** to handle missing Supabase gracefully

   - Checks if Supabase credentials are provided before initializing
   - Falls back to standalone mode if not configured
   - Logs warnings instead of crashing

3. **Created `app.py`** for Hugging Face Spaces

   - Entry point that HF Spaces expects
   - Imports the FastAPI app from `main.py`

4. **Updated Dockerfile** for HF Spaces compatibility

   - Uses `app:app` instead of `main:app`
   - Handles PORT environment variable from HF Spaces

5. **Port configuration** handles HF Spaces dynamic ports
   - Defaults to 8000 for local development
   - Automatically uses PORT env var if set (HF Spaces sets this)

## Deployment Steps

1. **Upload code to your HF Space**

   - Ensure all files are in the repository

2. **Set Environment Variables** (optional, in Space Settings → Secrets):

   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-key
   ```

3. **Wait for build** (first time takes 5-10 minutes for model download)

4. **Test the API**:
   ```bash
   curl https://your-username-spaces.hf.space/api/v1/health
   ```

## Standalone Mode Features

Without Supabase configured, the API supports:

- ✅ Health check endpoint
- ✅ Upload items with images and generate embeddings
- ✅ Get recommendations from uploaded items
- ❌ Cannot fetch items from Supabase database (use image_url parameter instead)
- ❌ Outfit recommendations require Supabase

## Files Changed

- `config.py` - Made Supabase optional
- `services/item_service.py` - Graceful Supabase handling
- `main.py` - Updated recommendations endpoint to accept image_url
- `app.py` - New file for HF Spaces entry point
- `Dockerfile` - Updated for HF Spaces

## Next Steps

1. Push your code to the HF Space repository
2. Set secrets if you want full Supabase integration
3. Monitor the build logs for any issues
4. Test endpoints once deployed

The API should now start successfully on Hugging Face Spaces! 🚀
