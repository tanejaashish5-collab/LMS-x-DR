-- ATLAS Test Fixtures Cleanup
-- Run this after integration testing to remove test data
-- Database: yozmayslzckaczdfohll (ATLAS Agent Swarm)

-- Delete test data in reverse order of dependencies

-- Delete test agent logs
DELETE FROM atlas_agent_logs
WHERE created_at >= CURRENT_DATE - INTERVAL '1 hour'
  AND agent IN ('SCOUT', 'ATLAS', 'MERCURY', 'VAULT')
  AND (input::text LIKE '%test-%' OR output::text LIKE '%test-%');

-- Delete test briefings
DELETE FROM atlas_briefings
WHERE id IN (
  SELECT id FROM atlas_briefings
  WHERE date = CURRENT_DATE
    AND content::text LIKE '%test-exp-%'
);

-- Delete test metrics
DELETE FROM atlas_metrics
WHERE experiment_id IN ('test-exp-1', 'test-exp-2');

-- Delete test budget ledger entries
DELETE FROM atlas_budget_ledger
WHERE experiment_id IN ('test-exp-1', 'test-exp-2')
   OR description LIKE 'Test%'
   OR (month_key = TO_CHAR(CURRENT_DATE, 'YYYY-MM')
       AND created_at >= CURRENT_DATE - INTERVAL '1 hour');

-- Delete test experiments
DELETE FROM atlas_experiments
WHERE id IN ('test-exp-1', 'test-exp-2');

-- Delete test opportunities
DELETE FROM atlas_opportunities
WHERE id IN ('test-opp-1', 'test-opp-2', 'test-opp-3');

-- Verify cleanup
SELECT
  'Cleanup complete. Remaining test records:' as status,
  (SELECT COUNT(*) FROM atlas_opportunities WHERE id LIKE 'test-%') as test_opportunities,
  (SELECT COUNT(*) FROM atlas_experiments WHERE id LIKE 'test-%') as test_experiments,
  (SELECT COUNT(*) FROM atlas_metrics WHERE experiment_id LIKE 'test-%') as test_metrics,
  (SELECT COUNT(*) FROM atlas_budget_ledger WHERE experiment_id LIKE 'test-%') as test_ledger;