# FashionCLIP Outfit Recommendation - Implementation Plan

## Overview

This document outlines the complete implementation plan for adding FashionCLIP-based outfit recommendations to StyleSnap.

## Architecture

### Components

1. **FastAPI Backend Service**
   - Handles image uploads
   - Generates FashionCLIP embeddings
   - Manages FAISS vector index
   - Provides recommendation API endpoints

2. **FAISS Vector Store**
   - Stores item embeddings for fast similarity search
   - Enables cosine similarity comparisons
   - Scales to thousands of items

3. **Supabase Integration**
   - Stores item metadata (category, user_id, etc.)
   - Syncs with existing clothes table
   - Optional: stores embedding backups

4. **Vue.js Frontend Integration**
   - Calls recommendation API
   - Displays recommendations
   - Integrates with outfit creator

## Implementation Steps

### Phase 1: Backend Setup (Week 1)

#### 1.1 Set Up FastAPI Service
- [x] Create FastAPI project structure
- [x] Configure environment variables
- [x] Set up CORS for Vue.js integration
- [x] Create health check endpoint

#### 1.2 FashionCLIP Integration
- [x] Install and configure FashionCLIP model
- [x] Create embedding extraction service
- [x] Implement batch processing for efficiency
- [x] Add image preprocessing

#### 1.3 FAISS Index Management
- [x] Initialize FAISS index (512 dimensions)
- [x] Implement add/remove/search operations
- [x] Add metadata mapping (FAISS ID → item info)
- [x] Persist index to disk

### Phase 2: API Endpoints (Week 1-2)

#### 2.1 Core Endpoints
- [x] `POST /api/v1/items/upload` - Upload and process item
- [x] `POST /api/v1/items/recommendations` - Get item recommendations
- [x] `POST /api/v1/outfits/recommend` - Get outfit recommendations
- [x] `DELETE /api/v1/items/{id}` - Remove item from index

#### 2.2 Advanced Features
- [ ] `GET /api/v1/items/{id}/similar` - Find similar items
- [ ] `POST /api/v1/batch/upload` - Batch upload items
- [ ] `GET /api/v1/stats` - Service statistics

### Phase 3: Database Integration (Week 2)

#### 3.1 Supabase Schema Updates
- [ ] Add embedding column (optional, for backup)
- [ ] Add faiss_id column for tracking
- [ ] Create migration script
- [ ] Update RLS policies if needed

#### 3.2 Sync Logic
- [ ] Create sync service for existing items
- [ ] Implement background job for new items
- [ ] Handle deletions and updates

### Phase 4: Frontend Integration (Week 2-3)

#### 4.1 Service Layer
- [ ] Create `fashionClipService.js`
- [ ] Integrate with existing `clothesService.js`
- [ ] Add error handling and retries

#### 4.2 UI Components
- [ ] Create `ItemRecommendations.vue` component
- [ ] Add recommendation cards
- [ ] Integrate with outfit creator
- [ ] Add loading states and error messages

#### 4.3 User Experience
- [ ] Show recommendations when viewing item
- [ ] "Get Recommendations" button in outfit creator
- [ ] Display similarity scores
- [ ] Allow adding recommendations to canvas

### Phase 5: Deployment & Optimization (Week 3-4)

#### 5.1 Deployment
- [ ] Deploy FastAPI service (Railway/Render/Fly.io)
- [ ] Configure persistent storage for FAISS
- [ ] Set up environment variables
- [ ] Configure CORS for production

#### 5.2 Performance
- [ ] Optimize model loading (caching)
- [ ] Implement request batching
- [ ] Add response caching
- [ ] Monitor performance metrics

#### 5.3 Monitoring
- [ ] Add logging
- [ ] Set up error tracking
- [ ] Monitor API response times
- [ ] Track recommendation quality

## Technical Details

### FashionCLIP Model
- **Model**: `patrickjohncyh/fashion-clip`
- **Embedding Dimension**: 512
- **Use Case**: Generate style-compatible embeddings
- **Performance**: ~100-200ms per image (CPU), ~20-50ms (GPU)

### FAISS Configuration
- **Index Type**: `IndexFlatIP` (Inner Product for cosine similarity)
- **Dimension**: 512
- **Normalization**: Embeddings normalized to unit vectors
- **Storage**: Persistent to disk, loaded on startup

### Recommendation Algorithm

1. **Item Recommendations**:
   - Query item's embedding
   - Search FAISS index for similar items
   - Filter by user_id and category
   - Return top K results by similarity

2. **Outfit Recommendations**:
   - Average embeddings of base items
   - Search for complementary categories
   - Return recommendations per category

### API Request/Response Examples

#### Upload Item
```bash
POST /api/v1/items/upload
Content-Type: multipart/form-data

file: <image>
item_id: "uuid-123"
user_id: "user-456"
category: "top"
```

#### Get Recommendations
```bash
POST /api/v1/items/recommendations
Content-Type: application/json

{
  "item_id": "uuid-123",
  "user_id": "user-456",
  "k": 10,
  "target_categories": ["bottom", "shoes"],
  "min_similarity": 0.5
}
```

## Scalability Considerations

### Current Limitations
- FAISS Flat index: O(n) search time
- In-memory model loading
- Single instance (no clustering)

### Future Improvements
- Upgrade to FAISS IVF index for faster search
- Model serving (TorchServe, etc.)
- Horizontal scaling with distributed FAISS
- Redis caching for frequent queries

## Security Considerations

1. **Authentication**: Validate user_id matches requesting user
2. **Image Validation**: Verify file types and sizes
3. **Rate Limiting**: Prevent abuse
4. **CORS**: Restrict to allowed origins

## Testing Strategy

1. **Unit Tests**: Model, FAISS operations
2. **Integration Tests**: API endpoints
3. **E2E Tests**: Full recommendation flow
4. **Performance Tests**: Load testing with many items

## Success Metrics

- **Accuracy**: User satisfaction with recommendations
- **Performance**: <500ms API response time
- **Uptime**: 99.9% availability
- **Usage**: % of users using recommendations

## Timeline

- **Week 1**: Backend setup, FashionCLIP integration
- **Week 2**: API endpoints, database integration
- **Week 3**: Frontend integration, UI components
- **Week 4**: Deployment, optimization, testing

## Dependencies

### Python
- FastAPI, Uvicorn
- FashionCLIP (Hugging Face)
- FAISS
- Supabase client
- PIL, NumPy

### Infrastructure
- FastAPI hosting (Railway/Render/Fly.io)
- Persistent storage for FAISS index
- Supabase database

## Cost Estimates

- **Hosting**: $20-50/month (Railway/Render)
- **Storage**: ~100MB per 10k items
- **Compute**: CPU sufficient for small scale, GPU recommended for production

