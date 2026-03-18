/* ─── Supabase table types derived from ATLAS Python agents ─── */

export interface AtlasOpportunity {
  id: string;
  title: string;
  source: string;
  source_url: string;
  description: string;
  category: string;
  target_vertical: string | null;
  haiku_filter_pass: boolean;
  sonnet_score: number | null;
  status: string;
  discovered_at: string;
  created_at: string;
}

export interface AtlasBudgetLedger {
  id: string;
  type: "spend" | "revenue";
  amount: number;
  experiment_id: string | null;
  agent: string;
  description: string;
  balance_after: number;
  month_key: string;
  created_at: string;
}

export interface AtlasBudgetSummary {
  month_key: string;
  total_deposited: number;
  total_spent: number;
  total_revenue: number;
  current_balance: number;
  transaction_count: number;
}

export interface AtlasExperiment {
  id: string;
  name: string;
  opportunity_id: string | null;
  status: string;
  budget_spent: number;
  landing_page_url: string | null;
  landing_page_html: string | null;
  distribution_channels: string[] | null;
  started_at: string | null;
  created_at: string;
}

export interface AtlasAgentLog {
  id: string;
  agent: string;
  action: string;
  input: string | null;
  output: string | null;
  model_used: string | null;
  tokens_in: number | null;
  tokens_out: number | null;
  cost_usd: number | null;
  status: string;
  created_at: string;
}

export interface AtlasPipelineItem {
  id: string;
  opportunity_id: string | null;
  title: string;
  vertical: string;
  stage: PipelineStage;
  value: number;
  contact: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export type PipelineStage =
  | "discovered"
  | "qualified"
  | "proposed"
  | "responded"
  | "closed"
  | "delivering";

export const PIPELINE_STAGES: { key: PipelineStage; label: string; color: string }[] = [
  { key: "discovered", label: "Discovered", color: "#6366f1" },
  { key: "qualified", label: "Qualified", color: "#8b5cf6" },
  { key: "proposed", label: "Proposed", color: "#22d3ee" },
  { key: "responded", label: "Responded", color: "#f59e0b" },
  { key: "closed", label: "Closed", color: "#34d399" },
  { key: "delivering", label: "Delivering", color: "#10b981" },
];

export const AGENT_COLORS: Record<string, string> = {
  scout: "#6366f1",
  vault: "#f59e0b",
  forge: "#ef4444",
  mercury: "#22d3ee",
};

export const AGENT_ICONS: Record<string, string> = {
  scout: "S",
  vault: "V",
  forge: "F",
  mercury: "M",
};
