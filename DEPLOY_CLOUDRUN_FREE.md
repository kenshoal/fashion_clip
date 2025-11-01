# Deploy to Google Cloud Run - 100% FREE!

## Free Tier Limits:
- ✅ **2 million requests/month** FREE
- ✅ **360,000 GB-seconds compute** FREE
- ✅ **Always free** - no credit card required for free tier
- ✅ Perfect for your API!

## Quick Deploy (5 commands):

```bash
# 1. Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash

# 2. Login
gcloud auth login

# 3. Create project (or use existing)
gcloud projects create fashion-clip-api --name="FashionCLIP API"

# 4. Set project
gcloud config set project fashion-clip-api

# 5. Deploy!
gcloud run deploy fashion-clip-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300
```

## That's It!

Your API will be at: `https://fashion-clip-api-[hash]-uc.a.run.app`

**100% FREE with generous limits!**

