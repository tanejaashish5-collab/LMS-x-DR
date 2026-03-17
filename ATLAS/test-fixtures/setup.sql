-- ATLAS Test Fixtures Setup
-- Run this before integration testing
-- Database: yozmayslzckaczdfohll (ATLAS Agent Swarm)

-- Test Fixtures as specified in Section 14 of the blueprint

-- 1. Three fake opportunities for testing filters
INSERT INTO atlas_opportunities (id, title, source, source_url, description, category, target_vertical, haiku_filter_pass, status, discovered_at)
VALUES
  -- Should pass Haiku filter (real automation pain)
  ('test-opp-1', 'Law firm spending 8 hours weekly on client intake forms', 'reddit', 'https://reddit.com/r/lawfirm/test1',
   'We are a 5-person law firm and our paralegal spends 8+ hours every week manually copying client intake forms from Typeform into our practice management system. There must be a better way!',
   'automation_service', 'Client Intake', true, 'haiku_filtered', NOW()),

  -- Should NOT pass filter (too vague)
  ('test-opp-2', 'Looking for automation tools', 'reddit', 'https://reddit.com/r/entrepreneur/test2',
   'Hey everyone, just wondering what automation tools you all use? Looking for recommendations.',
   'other', NULL, false, 'discovered', NOW()),

  -- Edge case (mentions automation but not a business need)
  ('test-opp-3', 'Built an automation for my hobby project', 'reddit', 'https://reddit.com/r/automation/test3',
   'Check out this cool n8n workflow I built to automatically water my plants based on soil moisture!',
   'other', NULL, false, 'discovered', NOW());

-- 2. One fake experiment with budget allocated
INSERT INTO atlas_experiments (id, opportunity_id, name, type, status, hypothesis, budget_allocated, budget_spent, total_revenue, ehs_current, launched_at)
VALUES
  ('test-exp-1', 'test-opp-1', 'Law Firm Intake Automator', 'landing_page', 'live',
   'Law firms will pay $2000 for automated client intake that saves 8 hours/week',
   30.00, 15.00, 0.00, 45.0, NOW() - INTERVAL '3 days');

-- 3. Seven days of fake metrics for EHS testing
INSERT INTO atlas_metrics (experiment_id, date, page_views, unique_visitors, avg_time_on_page, signups, purchases, revenue, ad_spend, organic_visits, paid_visits, ehs)
VALUES
  -- Day 1: Good start
  ('test-exp-1', CURRENT_DATE - INTERVAL '6 days', 25, 20, 45, 2, 0, 0, 5.00, 5, 15, 55),
  -- Day 2: Growing
  ('test-exp-1', CURRENT_DATE - INTERVAL '5 days', 35, 28, 52, 3, 0, 0, 5.00, 8, 20, 58),
  -- Day 3: Peak
  ('test-exp-1', CURRENT_DATE - INTERVAL '4 days', 45, 38, 68, 5, 1, 250.00, 5.00, 15, 23, 72),
  -- Day 4: Declining
  ('test-exp-1', CURRENT_DATE - INTERVAL '3 days', 30, 22, 41, 2, 0, 0, 5.00, 10, 12, 48),
  -- Day 5: Poor
  ('test-exp-1', CURRENT_DATE - INTERVAL '2 days', 15, 10, 28, 0, 0, 0, 5.00, 3, 7, 25),
  -- Day 6: Very poor (triggers EHS < 30)
  ('test-exp-1', CURRENT_DATE - INTERVAL '1 day', 8, 5, 15, 0, 0, 0, 5.00, 1, 4, 18),
  -- Day 7: Dead (should trigger kill)
  ('test-exp-1', CURRENT_DATE, 5, 3, 12, 0, 0, 0, 5.00, 0, 3, 15);

-- 4. High-performing experiment for scale testing
INSERT INTO atlas_experiments (id, opportunity_id, name, type, status, hypothesis, budget_allocated, budget_spent, total_revenue, ehs_current, launched_at)
VALUES
  ('test-exp-2', 'test-opp-1', 'Review Autopilot Pro', 'landing_page', 'live',
   'Local businesses will pay $29/mo for automated Google review responses',
   50.00, 35.00, 580.00, 85.0, NOW() - INTERVAL '7 days');

-- High performer metrics (EHS > 70)
INSERT INTO atlas_metrics (experiment_id, date, page_views, unique_visitors, avg_time_on_page, signups, purchases, revenue, ad_spend, organic_visits, paid_visits, ehs)
VALUES
  ('test-exp-2', CURRENT_DATE, 120, 95, 142, 12, 8, 232.00, 5.00, 60, 35, 85);

-- 5. Budget ledger entries for testing math
INSERT INTO atlas_budget_ledger (experiment_id, agent, amount, type, description, balance_after, month_key)
VALUES
  (NULL, 'VAULT', 250.00, 'budget_deposit', 'Monthly budget deposit', 250.00, TO_CHAR(CURRENT_DATE, 'YYYY-MM')),
  ('test-exp-1', 'MERCURY', -5.00, 'spend', 'Meta ads Day 1', 245.00, TO_CHAR(CURRENT_DATE, 'YYYY-MM')),
  ('test-exp-1', 'MERCURY', -5.00, 'spend', 'Meta ads Day 2', 240.00, TO_CHAR(CURRENT_DATE, 'YYYY-MM')),
  ('test-exp-1', 'FORGE', -2.50, 'spend', 'Sonnet API for landing page', 237.50, TO_CHAR(CURRENT_DATE, 'YYYY-MM')),
  ('test-exp-2', 'MERCURY', -35.00, 'spend', 'Week 1 ad spend', 202.50, TO_CHAR(CURRENT_DATE, 'YYYY-MM')),
  ('test-exp-2', 'VAULT', 580.00, 'revenue', 'Revenue from 20 subscriptions', 782.50, TO_CHAR(CURRENT_DATE, 'YYYY-MM')),
  ('test-exp-1', 'VAULT', 15.00, 'reallocation', 'Budget returned from killed experiment', 797.50, TO_CHAR(CURRENT_DATE, 'YYYY-MM'));

-- Create test agent logs
INSERT INTO atlas_agent_logs (agent, action, model_used, tokens_in, tokens_out, cost_usd, status)
VALUES
  ('SCOUT', 'opportunity_scan', 'claude-3-haiku', 1500, 300, 0.018, 'success'),
  ('SCOUT', 'deep_score', 'claude-3-5-sonnet', 800, 500, 0.15, 'success'),
  ('ATLAS', 'strategic_decision', 'claude-3-5-sonnet', 2000, 800, 0.30, 'success'),
  ('MERCURY', 'write_reddit_post', 'claude-3-haiku', 400, 200, 0.008, 'success'),
  ('VAULT', 'spend_blocked', NULL, 0, 0, 0.00, 'blocked');

-- Create a test briefing
INSERT INTO atlas_briefings (date, type, content, decisions, veto_status, planned_actions)
VALUES
  (CURRENT_DATE, 'daily',
   '{"portfolio_status": {"active_experiments": 2, "total_ehs": 65, "budget_remaining": 202.50}}',
   '[{"action": "kill", "target_id": "test-exp-1", "reason": "EHS below 20 for 3 days"}, {"action": "scale", "target_id": "test-exp-2", "reason": "Positive ROI"}]',
   'pending',
   '["Kill test-exp-1", "Double budget for test-exp-2", "Launch new AR Collections experiment"]');

-- Summary of test data created:
-- 3 opportunities (1 good, 1 bad, 1 edge case)
-- 2 experiments (1 failing, 1 succeeding)
-- 14 metrics rows (7 days x 2 experiments)
-- 7 budget ledger entries
-- 5 agent log entries
-- 1 pending briefing

SELECT 'Test fixtures loaded successfully' as status;