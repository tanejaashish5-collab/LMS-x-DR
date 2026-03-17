-- Add landing page columns to atlas_experiments table
-- Run this in Supabase SQL Editor

ALTER TABLE atlas_experiments
ADD COLUMN IF NOT EXISTS landing_page_url TEXT,
ADD COLUMN IF NOT EXISTS landing_page_html TEXT,
ADD COLUMN IF NOT EXISTS landing_page_deployed_at TIMESTAMPTZ;

-- Add comment
COMMENT ON COLUMN atlas_experiments.landing_page_url IS 'Deployed Vercel URL for the landing page';
COMMENT ON COLUMN atlas_experiments.landing_page_html IS 'Generated HTML content';
COMMENT ON COLUMN atlas_experiments.landing_page_deployed_at IS 'When the landing page was deployed';

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_experiments_landing_url ON atlas_experiments(landing_page_url) WHERE landing_page_url IS NOT NULL;
