-- ATLAS Evaluation Columns Migration
-- Adds quality tracking to proposals and content tables
-- Date: 2026-03-22

-- ===========================================
-- Proposal quality tracking
-- ===========================================
ALTER TABLE atlas_proposals ADD COLUMN IF NOT EXISTS quality_score NUMERIC;
ALTER TABLE atlas_proposals ADD COLUMN IF NOT EXISTS eval_score NUMERIC;
ALTER TABLE atlas_proposals ADD COLUMN IF NOT EXISTS eval_dimensions JSONB;
ALTER TABLE atlas_proposals ADD COLUMN IF NOT EXISTS was_revised BOOLEAN DEFAULT false;

-- ===========================================
-- Content quality tracking
-- ===========================================
ALTER TABLE atlas_content ADD COLUMN IF NOT EXISTS eval_score NUMERIC;
ALTER TABLE atlas_content ADD COLUMN IF NOT EXISTS eval_dimensions JSONB;

-- Allow 'needs_review' status for low-scoring content
ALTER TABLE atlas_content DROP CONSTRAINT IF EXISTS valid_content_status;
ALTER TABLE atlas_content
    ADD CONSTRAINT valid_content_status
    CHECK (status IN ('draft', 'needs_review', 'reviewed', 'posted', 'skipped'));

-- ===========================================
-- Conversion tracking view
-- ===========================================
CREATE OR REPLACE VIEW atlas_conversion_metrics AS
SELECT
    p.stage,
    COUNT(*) AS count,
    SUM(p.deal_value) AS total_value,
    AVG(pr.quality_score) AS avg_quality_score,
    AVG(pr.eval_score) AS avg_eval_score
FROM atlas_pipeline p
LEFT JOIN atlas_proposals pr ON pr.pipeline_id = p.id
GROUP BY p.stage;

-- ===========================================
-- Index for fast quality lookups
-- ===========================================
CREATE INDEX IF NOT EXISTS idx_proposals_quality ON atlas_proposals(quality_score);
CREATE INDEX IF NOT EXISTS idx_proposals_eval ON atlas_proposals(eval_score);
CREATE INDEX IF NOT EXISTS idx_content_eval ON atlas_content(eval_score);

SELECT 'Evaluation columns added successfully' AS status;
