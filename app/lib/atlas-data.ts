import { supabase, isSupabaseConfigured } from "./supabase";
import {
  mockOpportunities,
  mockBudgetSummary,
  mockBudgetLedger,
  mockExperiments,
  mockAgentLogs,
  mockPipeline,
} from "./mock-data";
import type {
  AtlasOpportunity,
  AtlasBudgetSummary,
  AtlasBudgetLedger,
  AtlasExperiment,
  AtlasAgentLog,
  AtlasPipelineItem,
} from "./atlas-types";

/* ─── Data source flag ─── */

export function isLive(): boolean {
  return isSupabaseConfigured() && supabase !== null;
}

/* ─── Opportunities ─── */

export async function getOpportunities(): Promise<AtlasOpportunity[]> {
  if (!isLive() || !supabase) return mockOpportunities;
  try {
    const { data, error } = await supabase
      .from("atlas_opportunities")
      .select("*")
      .eq("haiku_filter_pass", true)
      .order("sonnet_score", { ascending: false, nullsFirst: false });
    if (error) throw error;
    return (data as AtlasOpportunity[]) ?? mockOpportunities;
  } catch {
    return mockOpportunities;
  }
}

export async function getTopOpportunities(limit = 5): Promise<AtlasOpportunity[]> {
  if (!isLive() || !supabase) return mockOpportunities.slice(0, limit);
  try {
    const { data, error } = await supabase
      .from("atlas_opportunities")
      .select("*")
      .eq("haiku_filter_pass", true)
      .not("sonnet_score", "is", null)
      .order("sonnet_score", { ascending: false })
      .limit(limit);
    if (error) throw error;
    return (data as AtlasOpportunity[]) ?? mockOpportunities.slice(0, limit);
  } catch {
    return mockOpportunities.slice(0, limit);
  }
}

/* ─── Budget ─── */

export async function getBudgetSummary(): Promise<AtlasBudgetSummary> {
  if (!isLive() || !supabase) return mockBudgetSummary;
  try {
    const monthKey = new Date().toISOString().slice(0, 7);
    const { data, error } = await supabase
      .from("atlas_budget_summary")
      .select("*")
      .eq("month_key", monthKey)
      .single();
    if (error) throw error;
    return (data as AtlasBudgetSummary) ?? mockBudgetSummary;
  } catch {
    return mockBudgetSummary;
  }
}

export async function getBudgetLedger(): Promise<AtlasBudgetLedger[]> {
  if (!isLive() || !supabase) return mockBudgetLedger;
  try {
    const monthKey = new Date().toISOString().slice(0, 7);
    const { data, error } = await supabase
      .from("atlas_budget_ledger")
      .select("*")
      .eq("month_key", monthKey)
      .order("created_at", { ascending: false });
    if (error) throw error;
    return (data as AtlasBudgetLedger[]) ?? mockBudgetLedger;
  } catch {
    return mockBudgetLedger;
  }
}

/* ─── Experiments ─── */

export async function getExperiments(): Promise<AtlasExperiment[]> {
  if (!isLive() || !supabase) return mockExperiments;
  try {
    const { data, error } = await supabase
      .from("atlas_experiments")
      .select("*")
      .order("created_at", { ascending: false });
    if (error) throw error;
    return (data as AtlasExperiment[]) ?? mockExperiments;
  } catch {
    return mockExperiments;
  }
}

/* ─── Agent Logs ─── */

export async function getAgentLogs(limit = 50): Promise<AtlasAgentLog[]> {
  if (!isLive() || !supabase) return mockAgentLogs.slice(0, limit);
  try {
    const { data, error } = await supabase
      .from("atlas_agent_logs")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(limit);
    if (error) throw error;
    return (data as AtlasAgentLog[]) ?? mockAgentLogs.slice(0, limit);
  } catch {
    return mockAgentLogs.slice(0, limit);
  }
}

export async function getRecentLogs(hours = 24): Promise<AtlasAgentLog[]> {
  if (!isLive() || !supabase) {
    const cutoff = new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();
    return mockAgentLogs.filter((l) => l.created_at >= cutoff);
  }
  try {
    const since = new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();
    const { data, error } = await supabase
      .from("atlas_agent_logs")
      .select("*")
      .gte("created_at", since)
      .order("created_at", { ascending: false });
    if (error) throw error;
    return (data as AtlasAgentLog[]) ?? [];
  } catch {
    return [];
  }
}

/* ─── Pipeline ─── */

export async function getPipeline(): Promise<AtlasPipelineItem[]> {
  if (!isLive() || !supabase) return mockPipeline;
  try {
    const { data, error } = await supabase
      .from("atlas_pipeline")
      .select("*")
      .order("updated_at", { ascending: false });
    if (error) throw error;
    return (data as AtlasPipelineItem[]) ?? mockPipeline;
  } catch {
    return mockPipeline;
  }
}

/* ─── Dashboard Stats (aggregated) ─── */

export interface DashboardStats {
  totalOpportunities: number;
  budgetRemaining: number;
  budgetLimit: number;
  activeExperiments: number;
  distributionsSent: number;
  totalSpent: number;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const [opportunities, budget, experiments, logs] = await Promise.all([
    getOpportunities(),
    getBudgetSummary(),
    getExperiments(),
    getAgentLogs(200),
  ]);

  const distributionLogs = logs.filter(
    (l) => l.agent === "mercury" && l.action.startsWith("distribute_")
  );

  return {
    totalOpportunities: opportunities.length,
    budgetRemaining: budget.current_balance,
    budgetLimit: budget.total_deposited,
    activeExperiments: experiments.filter(
      (e) => e.status === "running" || e.status === "active"
    ).length,
    distributionsSent: distributionLogs.length,
    totalSpent: budget.total_spent,
  };
}
