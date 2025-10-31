# Integration Guide: FashionCLIP API with Vue.js Frontend

This guide explains how to integrate the FashionCLIP recommendation API with your Vue.js application.

## 1. Update Vue.js Service Layer

Create a new service file for the FashionCLIP API:

```javascript
// src/services/fashionClipService.js
const FASHION_CLIP_API_URL = import.meta.env.VITE_FASHION_CLIP_API_URL || 'http://localhost:8000'

export class FashionClipService {
  /**
   * Upload item image and generate embedding
   */
  async uploadItemForEmbedding(itemId, userId, category, imageFile, imageUrl, name) {
    const formData = new FormData()
    formData.append('file', imageFile)
    formData.append('item_id', itemId)
    formData.append('user_id', userId)
    formData.append('category', category)
    if (imageUrl) formData.append('image_url', imageUrl)
    if (name) formData.append('name', name)

    const response = await fetch(`${FASHION_CLIP_API_URL}/api/v1/items/upload`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error('Failed to upload item for embedding')
    }

    return response.json()
  }

  /**
   * Get recommendations for an item
   */
  async getItemRecommendations(itemId, userId, options = {}) {
    const {
      k = 10,
      targetCategories = null,
      minSimilarity = 0.5
    } = options

    const response = await fetch(`${FASHION_CLIP_API_URL}/api/v1/items/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        item_id: itemId,
        user_id: userId,
        k,
        target_categories: targetCategories,
        min_similarity: minSimilarity
      })
    })

    if (!response.ok) {
      throw new Error('Failed to get recommendations')
    }

    return response.json()
  }

  /**
   * Get complete outfit recommendations
   */
  async getOutfitRecommendations(baseItemIds, userId, kPerCategory = 3) {
    const response = await fetch(`${FASHION_CLIP_API_URL}/api/v1/outfits/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_items: baseItemIds,
        user_id: userId,
        k_per_category: kPerCategory
      })
    })

    if (!response.ok) {
      throw new Error('Failed to get outfit recommendations')
    }

    return response.json()
  }

  /**
   * Remove item from index
   */
  async removeItemFromIndex(itemId) {
    const response = await fetch(`${FASHION_CLIP_API_URL}/api/v1/items/${itemId}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      throw new Error('Failed to remove item from index')
    }

    return response.json()
  }
}
```

## 2. Integrate with ClothesService

Update your existing `clothesService.js` to automatically generate embeddings when items are uploaded:

```javascript
// src/services/clothesService.js
import { FashionClipService } from './fashionClipService'

const fashionClipService = new FashionClipService()

export class ClothesService {
  // ... existing code ...

  async addClothingItem(itemData, imageFile) {
    // 1. Upload to Cloudinary (existing code)
    const imageUrl = await this.uploadToCloudinary(imageFile)
    
    // 2. Save to Supabase (existing code)
    const { data: item, error } = await supabase
      .from('clothes')
      .insert({
        ...itemData,
        image_url: imageUrl
      })
      .select()
      .single()

    if (error) throw error

    // 3. Generate embedding (NEW)
    try {
      await fashionClipService.uploadItemForEmbedding(
        item.id,
        item.user_id,
        item.category,
        imageFile,
        imageUrl,
        item.name
      )
    } catch (error) {
      console.warn('Failed to generate embedding:', error)
      // Don't fail the entire operation if embedding fails
    }

    return item
  }

  async deleteClothingItem(itemId) {
    // 1. Delete from Supabase
    const { error } = await supabase
      .from('clothes')
      .delete()
      .eq('id', itemId)

    if (error) throw error

    // 2. Remove from FAISS index
    try {
      await fashionClipService.removeItemFromIndex(itemId)
    } catch (error) {
      console.warn('Failed to remove from index:', error)
    }
  }
}
```

## 3. Add Recommendation UI Component

```vue
<!-- src/components/ItemRecommendations.vue -->
<template>
  <div class="recommendations">
    <button 
      @click="loadRecommendations"
      :disabled="loading"
      class="btn-recommend"
    >
      <Sparkles v-if="!loading" class="w-4 h-4" />
      <span v-if="loading">Loading...</span>
      <span v-else>Get AI Recommendations</span>
    </button>

    <div v-if="recommendations.length > 0" class="recommendations-grid">
      <div 
        v-for="rec in recommendations" 
        :key="rec.item_id"
        class="recommendation-card"
      >
        <img :src="rec.image_url" :alt="rec.name" />
        <div class="info">
          <h4>{{ rec.name }}</h4>
          <p class="category">{{ rec.category }}</p>
          <p class="similarity">{{ Math.round(rec.similarity * 100) }}% match</p>
        </div>
        <button @click="addToOutfit(rec)">Add to Outfit</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FashionClipService } from '@/services/fashionClipService'
import { Sparkles } from 'lucide-vue-next'

const props = defineProps({
  itemId: String,
  userId: String,
  targetCategories: Array
})

const fashionClipService = new FashionClipService()
const recommendations = ref([])
const loading = ref(false)

const loadRecommendations = async () => {
  loading.value = true
  try {
    const result = await fashionClipService.getItemRecommendations(
      props.itemId,
      props.userId,
      {
        targetCategories: props.targetCategories,
        k: 10,
        minSimilarity: 0.5
      }
    )
    recommendations.value = result.recommendations
  } catch (error) {
    console.error('Failed to load recommendations:', error)
  } finally {
    loading.value = false
  }
}

const addToOutfit = (item) => {
  emit('add-item', item)
}

const emit = defineEmits(['add-item'])
</script>
```

## 4. Environment Variables

Add to your `.env.local`:

```env
VITE_FASHION_CLIP_API_URL=http://localhost:8000
```

For production:

```env
VITE_FASHION_CLIP_API_URL=https://fashion-clip-api.yourdomain.com
```

## 5. Deployment Architecture

```
┌─────────────────────┐
│   Vercel/Netlify    │  (Vue.js Frontend)
└──────────┬──────────┘
           │
           │ HTTPS
           │
┌──────────▼──────────────────┐
│   Railway/Render/Fly.io     │  (FastAPI Backend)
│   - FashionCLIP API         │
│   - FAISS Index Storage      │
└──────────┬───────────────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼───┐    ┌────▼─────┐
│FAISS  │    │ Supabase │
│Index  │    │ (DB)     │
└───────┘    └──────────┘
```

## 6. Deployment Steps

### Backend (FastAPI):
1. Deploy to Railway, Render, or Fly.io
2. Set environment variables
3. Run migration script to index existing items
4. Set up persistent storage for FAISS index

### Frontend (Vue.js):
1. Update environment variables
2. Deploy as usual (Vercel/Netlify)
3. Update CORS settings in FastAPI if needed

## 7. Performance Considerations

- **FAISS Index**: Store on persistent volume (Railway volumes, etc.)
- **Model Loading**: First request may be slow (cold start)
- **Caching**: Consider caching embeddings for frequently accessed items
- **Batch Processing**: Use batch upload endpoint for bulk operations

## 8. Monitoring

Monitor:
- API response times
- FAISS index size
- Memory usage (model loading)
- Error rates

