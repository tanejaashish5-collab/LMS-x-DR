"use client";

import { useState, useEffect, useMemo } from "react";
import type { AtlasBudgetSummary, AtlasBudgetLedger } from "@/app/lib/atlas-types";
import { AGENT_COLORS } from "@/app/lib/atlas-types";
import { mockBudgetSummary, mockBudgetLedger } from "@/app/lib/mock-data";

export default function BudgetPage() {
  const [summary, setSummary] = useState<AtlasBudgetSummary | null>(null);
  const [ledger, setLedger] = useState<AtlasBudgetLedger[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/atlas?resource=budget");
        const json = await res.json();
        setSummary(json.data?.summary ?? mockBudgetSummary);
        setLedger(json.data?.ledger ?? mockBudgetLedger);
        setLive(json.live ?? false);
      } catch {
        setSummary(mockBudgetSummary);
        setLedger(mockBudgetLedger);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const agentSpend = useMemo(() => {
    const byAgent: Record<string, number> = {};
    for (const txn of ledger) {
      if (txn.type === "spend") {
        byAgent[txn.agent] = (byAgent[txn.agent] ?? 0) + txn.amount;
      }
    }
    return byAgent;
  }, [ledger]);

  // Estimate real API cost — must be before early return (React hooks rule)
  const realCostEstimate = useMemo(() => {
    let estimate = 0;
    for (const txn of ledger) {
      if (txn.type !== "spend") continue;
      if (txn.agent === "closer") estimate += 0.03;
      else if (txn.agent === "content_creator") estimate += 0.01;
      else if (txn.agent === "scout") estimate += 0.02;
      else if (txn.agent === "forge") estimate += 0.10;
      else if (txn.agent === "mercury") estimate += 0.01;
      else estimate += 0.02;
    }
    return estimate;
  }, [ledger]);

  if (loading || !summary) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--text-muted)]">Loading budget...</div>
      </div>
    );
  }

  const percentSpent = summary.total_deposited > 0
    ? (summary.total_spent / summary.total_deposited) * 100
    : 0;
  const conservationMode = percentSpent >= 80;
  const monthlyLimit = 250;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Budget</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            Vault guardian -- {summary.month_key}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {conservationMode && (
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-rose)]/10 text-[var(--accent-rose)]">
              Conservation Mode
            </span>
          )}
          {!live && (
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]">
              Demo Data
            </span>
          )}
        </div>
      </div>

      {/* Budget Gauge */}
      <div className="glass rounded-xl p-6 mb-6">
        <div className="flex items-end justify-between mb-4">
          <div>
            <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-1">Remaining</div>
            <div className="text-4xl font-bold text-[var(--accent-emerald)]">
              ${summary.current_balance.toFixed(2)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-1">Internal Budget Used</div>
            <div className="text-2xl font-bold text-[var(--text-secondary)]">
              ${summary.total_spent.toFixed(2)}
            </div>
            <div className="text-[10px] text-[var(--text-muted)] mt-0.5">Reserved by Vault</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-1">Real API Cost</div>
            <div className="text-2xl font-bold text-[var(--accent-cyan,#22d3ee)]">
              ${realCostEstimate.toFixed(2)}
            </div>
            <div className="text-[10px] text-[var(--text-muted)] mt-0.5">Est. Anthropic bill</div>
          </div>
        </div>

        {/* Full gauge bar */}
        <div className="relative w-full h-6 rounded-full bg-white/5 overflow-hidden mb-2">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${Math.min(percentSpent, 100)}%`,
              background:
                percentSpent > 80
                  ? "var(--accent-rose)"
                  : percentSpent > 50
                  ? "var(--accent-amber)"
                  : "var(--accent-emerald)",
            }}
          />
          {/* 80% mark */}
          <div
            className="absolute top-0 bottom-0 w-px bg-[var(--accent-rose)]/50"
            style={{ left: "80%" }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-[var(--text-muted)]">
          <span>$0</span>
          <span className="text-[var(--accent-rose)]">$200 (80%)</span>
          <span>${monthlyLimit}</span>
        </div>
      </div>

      {/* Agent Breakdown */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {(["scout", "vault", "forge", "mercury", "closer", "content_creator"] as const).map((agent) => {
          const spent = agentSpend[agent] ?? 0;
          return (
            <div key={agent} className="glass rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <div
                  className="w-7 h-7 rounded-md flex items-center justify-center text-xs font-bold"
                  style={{
                    background: `${AGENT_COLORS[agent]}20`,
                    color: AGENT_COLORS[agent],
                  }}
                >
                  {agent[0].toUpperCase()}
                </div>
                <span className="text-sm font-medium capitalize">{agent}</span>
              </div>
              <div className="text-xl font-bold">${spent.toFixed(2)}</div>
              <div className="text-xs text-[var(--text-muted)]">
                {summary.total_spent > 0
                  ? `${((spent / summary.total_spent) * 100).toFixed(0)}% of total`
                  : "0% of total"}
              </div>
            </div>
          );
        })}
      </div>

      {/* Transaction Ledger */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-white/5">
          <h2 className="font-semibold">Transaction Ledger</h2>
          <p className="text-xs text-[var(--text-muted)] mt-0.5">{ledger.length} transactions this month</p>
        </div>
        <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-[var(--bg-card)]">
              <tr className="border-b border-white/5">
                <th className="text-left px-4 py-2.5 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium">Date</th>
                <th className="text-left px-4 py-2.5 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium">Agent</th>
                <th className="text-left px-4 py-2.5 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium hidden md:table-cell">Description</th>
                <th className="text-right px-4 py-2.5 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium">Amount</th>
                <th className="text-right px-4 py-2.5 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium hidden lg:table-cell">Balance</th>
              </tr>
            </thead>
            <tbody>
              {ledger.map((txn) => (
                <tr key={txn.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                  <td className="px-4 py-2.5 text-xs text-[var(--text-muted)] whitespace-nowrap">
                    {new Date(txn.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className="px-2 py-0.5 rounded text-xs font-medium capitalize"
                      style={{
                        background: `${AGENT_COLORS[txn.agent] ?? "#666"}15`,
                        color: AGENT_COLORS[txn.agent] ?? "#666",
                      }}
                    >
                      {txn.agent}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-[var(--text-secondary)] text-xs hidden md:table-cell max-w-[300px] truncate">
                    {txn.description}
                  </td>
                  <td className={`px-4 py-2.5 text-right font-medium text-xs ${
                    txn.type === "spend" ? "text-[var(--accent-rose)]" : "text-[var(--accent-emerald)]"
                  }`}>
                    {txn.type === "spend" ? "-" : "+"}${txn.amount.toFixed(2)}
                  </td>
                  <td className="px-4 py-2.5 text-right text-xs text-[var(--text-muted)] hidden lg:table-cell">
                    ${txn.balance_after.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
