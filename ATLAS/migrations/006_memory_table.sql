-- ATLAS Agent Memory System
-- Persistent memory for agent learning across runs.
-- Keyed by (agent, memory_type, key) with upsert support.

CREATE TABLE IF NOT EXISTS atlas_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    confidence NUMERIC DEFAULT 0.8,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    UNIQUE(agent, memory_type, key)
);

CREATE INDEX IF NOT EXISTS idx_memory_agent ON atlas_memory(agent);
CREATE INDEX IF NOT EXISTS idx_memory_type ON atlas_memory(agent, memory_type);
