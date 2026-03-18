"use client";

import { useState, useEffect, useMemo } from "react";
import type { AtlasAgentLog } from "@/app/lib/atlas-types";
import { AGENT_COLORS } from "@/app/lib/atlas-types";
import { mockAgentLogs } from "@/app/lib/mock-data";

function formatTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function AgentLogsPage() {
  const [logs, setLogs] = useState<AtlasAgentLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);
  const [filterAgent, setFilterAgent] = useState("all");

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/atlas?resource=logs");
        const json = await res.json();
        setLogs(json.data ?? mockAgentLogs);
        setLive(json.live ?? false);
      } catch {
        setLogs(mockAgentLogs);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filtered = useMemo(() => {
    if (filterAgent === "all") return logs;
    return logs.filter((l) => l.agent === filterAgent);
  }, [logs, filterAgent]);

  const agentStats = useMemo(() => {
    const stats: Record<string, { count: number; cost: number; lastRun: string; successes: number; failures: number }> = {};
    for (const log of logs) {
      if (!stats[log.agent]) {
        stats[log.agent] = { count: 0, cost: 0, lastRun: log.created_at, successes: 0, failures: 0 };
      }
      stats[log.agent].count++;
      stats[log.agent].cost += log.cost_usd ?? 0;
      if (log.created_at > stats[log.agent].lastRun) {
        stats[log.agent].lastRun = log.created_at;
      }
      if (log.status === "success") stats[log.agent].successes++;
      if (log.status === "blocked" || log.status === "failed") stats[log.agent].failures++;
    }
    return stats;
  }, [logs]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--text-muted)]">Loading agent logs...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Agent Logs</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            {filtered.length} events from all agents
          </p>
        </div>
        {!live && (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]">
            Demo Data
          </span>
        )}
      </div>

      {/* Agent Status Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {(["scout", "vault", "forge", "mercury"] as const).map((agent) => {
          const s = agentStats[agent];
          return (
            <button
              key={agent}
              onClick={() => setFilterAgent(filterAgent === agent ? "all" : agent)}
              className={`glass rounded-xl p-4 text-left transition-all cursor-pointer ${
                filterAgent === agent ? "ring-2 ring-[var(--accent-blue)]/30" : ""
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
                  style={{
                    background: `${AGENT_COLORS[agent]}20`,
                    color: AGENT_COLORS[agent],
                  }}
                >
                  {agent[0].toUpperCase()}
                </div>
                <div>
                  <span className="text-sm font-semibold capitalize">{agent}</span>
                  {s && (
                    <div className="text-[10px] text-[var(--text-muted)]">
                      Last: {formatTime(s.lastRun)}
                    </div>
                  )}
                </div>
              </div>
              {s ? (
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-[var(--text-secondary)]">{s.count} actions</span>
                  <span className="text-[var(--accent-emerald)]">{s.successes} ok</span>
                  {s.failures > 0 && (
                    <span className="text-[var(--accent-rose)]">{s.failures} fail</span>
                  )}
                </div>
              ) : (
                <div className="text-xs text-[var(--text-muted)]">No activity</div>
              )}
            </button>
          );
        })}
      </div>

      {/* Filter indicator */}
      {filterAgent !== "all" && (
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm text-[var(--text-secondary)]">Filtering by:</span>
          <span
            className="px-2 py-0.5 rounded text-xs font-medium capitalize"
            style={{
              background: `${AGENT_COLORS[filterAgent] ?? "#666"}15`,
              color: AGENT_COLORS[filterAgent] ?? "#666",
            }}
          >
            {filterAgent}
          </span>
          <button
            onClick={() => setFilterAgent("all")}
            className="text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
          >
            Clear
          </button>
        </div>
      )}

      {/* Timeline */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="divide-y divide-white/5 max-h-[600px] overflow-y-auto">
          {filtered.map((log) => (
            <div key={log.id} className="px-5 py-4 hover:bg-white/[0.02] transition-colors">
              <div className="flex items-start gap-3">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
                  style={{
                    background: `${AGENT_COLORS[log.agent] ?? "#666"}20`,
                    color: AGENT_COLORS[log.agent] ?? "#666",
                  }}
                >
                  {log.agent[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-medium capitalize">{log.agent}</span>
                    <span className="text-sm text-[var(--text-secondary)]">
                      {log.action.replace(/_/g, " ")}
                    </span>
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                        log.status === "success"
                          ? "bg-[var(--accent-emerald)]/10 text-[var(--accent-emerald)]"
                          : log.status === "blocked"
                          ? "bg-[var(--accent-rose)]/10 text-[var(--accent-rose)]"
                          : "bg-white/5 text-[var(--text-muted)]"
                      }`}
                    >
                      {log.status}
                    </span>
                  </div>
                  {log.input && (
                    <div className="text-xs text-[var(--text-muted)] mt-1">{log.input}</div>
                  )}
                  {log.output && (
                    <div className="text-xs text-[var(--text-secondary)] mt-0.5 break-words">
                      {log.output.length > 120 ? log.output.slice(0, 120) + "..." : log.output}
                    </div>
                  )}
                  <div className="flex items-center gap-3 mt-1.5 text-[10px] text-[var(--text-muted)]">
                    <span>{new Date(log.created_at).toLocaleString()}</span>
                    {log.model_used && <span>{log.model_used.replace("claude-3-", "").replace("claude-3-5-", "")}</span>}
                    {log.cost_usd !== null && log.cost_usd > 0 && <span>${log.cost_usd.toFixed(4)}</span>}
                    {log.tokens_in !== null && (
                      <span>{log.tokens_in}in / {log.tokens_out}out tokens</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="px-5 py-8 text-center text-[var(--text-muted)]">
              No logs match current filter
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
