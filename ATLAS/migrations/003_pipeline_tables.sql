-- ATLAS Pipeline Tables Migration
-- Creates tables for the CLOSER agent sales pipeline
-- Run against: yozmayslzckaczdfohll (ATLAS Agent Swarm)
-- Date: 2026-03-18

-- ===========================================
-- Pipeline Tracking
-- ===========================================
CREATE TABLE IF NOT EXISTS atlas_pipeline (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    opportunity_id UUID REFERENCES atlas_opportunities(id),
    stage TEXT NOT NULL DEFAULT 'discovered',
    qualified_at TIMESTAMPTZ,
    proposed_at TIMESTAMPTZ,
    responded_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    deal_value NUMERIC,
    currency TEXT DEFAULT 'AUD',
    notes TEXT,
    contact_email TEXT,
    contact_name TEXT,
    company_name TEXT,
    last_followup_at TIMESTAMPTZ,
    followup_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast stage lookups
CREATE INDEX IF NOT EXISTS idx_pipeline_stage ON atlas_pipeline(stage);
CREATE INDEX IF NOT EXISTS idx_pipeline_opportunity ON atlas_pipeline(opportunity_id);

-- ===========================================
-- Proposals
-- ===========================================
CREATE TABLE IF NOT EXISTS atlas_proposals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pipeline_id UUID REFERENCES atlas_pipeline(id),
    opportunity_id UUID REFERENCES atlas_opportunities(id),
    proposal_type TEXT DEFAULT 'initial',  -- 'initial', 'revised', 'final'
    content JSONB,        -- Full proposal content
    pricing JSONB,        -- {basic: {price, features}, pro: {...}, enterprise: {...}}
    roi_estimate JSONB,   -- ROI projection data
    sent_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    status TEXT DEFAULT 'draft',  -- draft, sent, opened, accepted, rejected
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_proposals_pipeline ON atlas_proposals(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON atlas_proposals(status);

-- ===========================================
-- Email Outreach Tracking
-- ===========================================
CREATE TABLE IF NOT EXISTS atlas_outreach (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pipeline_id UUID REFERENCES atlas_pipeline(id),
    email_type TEXT,  -- 'intro', 'proposal', 'followup_1', 'followup_2', 'followup_3', 'close'
    subject TEXT,
    body TEXT,
    to_email TEXT,
    from_email TEXT DEFAULT 'ashish@forgevoice.studio',
    sent_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    status TEXT DEFAULT 'draft',  -- draft, sent, opened, replied, bounced
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_outreach_pipeline ON atlas_outreach(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_outreach_status ON atlas_outreach(status);

-- ===========================================
-- Communication Log
-- ===========================================
CREATE TABLE IF NOT EXISTS atlas_communications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pipeline_id UUID REFERENCES atlas_pipeline(id),
    channel TEXT,      -- 'email', 'reddit_dm', 'linkedin', 'call', 'meeting'
    direction TEXT,    -- 'outbound', 'inbound'
    subject TEXT,
    content TEXT,
    sentiment TEXT,    -- 'positive', 'neutral', 'negative'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comms_pipeline ON atlas_communications(pipeline_id);

-- ===========================================
-- Updated_at trigger for pipeline
-- ===========================================
CREATE OR REPLACE FUNCTION update_pipeline_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_pipeline_updated_at ON atlas_pipeline;
CREATE TRIGGER trigger_pipeline_updated_at
    BEFORE UPDATE ON atlas_pipeline
    FOR EACH ROW
    EXECUTE FUNCTION update_pipeline_updated_at();

-- ===========================================
-- Pipeline stage validation
-- ===========================================
ALTER TABLE atlas_pipeline
    DROP CONSTRAINT IF EXISTS valid_pipeline_stage;

ALTER TABLE atlas_pipeline
    ADD CONSTRAINT valid_pipeline_stage
    CHECK (stage IN (
        'discovered',
        'qualified',
        'proposed',
        'responded',
        'negotiating',
        'closed_won',
        'closed_lost',
        'delivering'
    ));

-- ===========================================
-- Proposal status validation
-- ===========================================
ALTER TABLE atlas_proposals
    DROP CONSTRAINT IF EXISTS valid_proposal_status;

ALTER TABLE atlas_proposals
    ADD CONSTRAINT valid_proposal_status
    CHECK (status IN ('draft', 'sent', 'opened', 'accepted', 'rejected'));

-- ===========================================
-- Outreach status validation
-- ===========================================
ALTER TABLE atlas_outreach
    DROP CONSTRAINT IF EXISTS valid_outreach_status;

ALTER TABLE atlas_outreach
    ADD CONSTRAINT valid_outreach_status
    CHECK (status IN ('draft', 'sent', 'opened', 'replied', 'bounced'));

SELECT 'Pipeline tables created successfully' AS status;
