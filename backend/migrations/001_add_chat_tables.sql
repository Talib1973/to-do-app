-- Migration: Add conversations and messages tables for AI chatbot feature
-- Date: 2026-02-07
-- Description: Creates conversations and messages tables with proper indexes and foreign keys

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on conversations table
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create composite index on messages table (CRITICAL for performance)
-- This index supports: user authorization + conversation filtering + chronological ordering
-- Single index scan for query: "Get all messages in conversation X for user Y, ordered by time"
CREATE INDEX IF NOT EXISTS idx_messages_user_conv_time ON messages(user_id, conversation_id, created_at ASC);

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Chat sessions between authenticated users and AI chatbot';
COMMENT ON TABLE messages IS 'Individual messages within conversations (user or assistant)';
COMMENT ON INDEX idx_messages_user_conv_time IS 'Composite index for fast message retrieval with user scoping (~10x faster than separate indexes)';
