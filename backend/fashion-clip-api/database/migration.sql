-- Migration to add embedding support to clothes table
-- Run this in your Supabase SQL editor

-- Optional: Add embedding column to store backup embeddings
-- (FAISS is primary, but DB backup is useful)
-- This requires pgvector extension

-- Enable pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to clothes table (optional - for backup)
ALTER TABLE clothes 
ADD COLUMN IF NOT EXISTS embedding vector(512);

-- Create index for similarity search in PostgreSQL (optional)
-- FAISS is faster, but this can be useful for backup queries
CREATE INDEX IF NOT EXISTS clothes_embedding_idx 
ON clothes 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Add metadata columns if needed
ALTER TABLE clothes
ADD COLUMN IF NOT EXISTS faiss_id INTEGER,
ADD COLUMN IF NOT EXISTS embedding_generated_at TIMESTAMP WITH TIME ZONE;

-- Create index on faiss_id for faster lookups
CREATE INDEX IF NOT EXISTS clothes_faiss_id_idx ON clothes(faiss_id);

