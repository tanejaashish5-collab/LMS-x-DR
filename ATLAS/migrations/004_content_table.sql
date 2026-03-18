-- ATLAS Content Table for Content Creator Agent
-- Stores LinkedIn and Instagram content drafts, scheduled posts, and engagement metrics

CREATE TABLE IF NOT EXISTS atlas_content (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pillar TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'both',
    topic TEXT NOT NULL,
    headline TEXT,
    body TEXT NOT NULL,
    hashtags TEXT,
    carousel_slides JSONB,
    status TEXT DEFAULT 'draft',
    scheduled_for DATE,
    posted_at TIMESTAMPTZ,
    engagement JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_status ON atlas_content(status);
CREATE INDEX IF NOT EXISTS idx_content_scheduled ON atlas_content(scheduled_for);

ALTER TABLE atlas_content
    ADD CONSTRAINT valid_content_pillar
    CHECK (pillar IN ('industry', 'behind_scenes', 'value_bomb', 'social_proof'));

ALTER TABLE atlas_content
    ADD CONSTRAINT valid_content_platform
    CHECK (platform IN ('linkedin', 'instagram', 'both'));

ALTER TABLE atlas_content
    ADD CONSTRAINT valid_content_status
    CHECK (status IN ('draft', 'reviewed', 'posted', 'skipped'));
