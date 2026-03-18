"use client";

import { useState, useEffect, useMemo } from "react";
import type { AtlasAgentLog } from "@/app/lib/atlas-types";
import { mockAgentLogs } from "@/app/lib/mock-data";

const CHANNEL_COLORS: Record<string, string> = {
  reddit: "#FF4500",
  email: "#6366f1",
  meta_ads: "#1877F2",
  google_ads: "#34A853",
};

function parseDistributionOutput(output: string | null): Record<string, string> | null {
  if (!output) return null;
  try {
    return JSON.parse(output);
  } catch {
    return null;
  }
}

export default function DistributionPage() {
  const [logs, setLogs] = useState<AtlasAgentLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);

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

  const distributionLogs = useMemo(() => {
    return logs.filter(
      (l) => l.agent === "mercury" && l.action.startsWith("distribute_")
    );
  }, [logs]);

  const channelCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const log of distributionLogs) {
      const channel = log.action.replace("distribute_", "");
      counts[channel] = (counts[channel] ?? 0) + 1;
    }
    return counts;
  }, [distributionLogs]);

  const totalCost = useMemo(() => {
    return distributionLogs.reduce((sum, l) => sum + (l.cost_usd ?? 0), 0);
  }, [distributionLogs]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--text-muted)]">Loading distributions...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Distribution</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            Mercury channel performance
          </p>
        </div>
        {!live && (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]">
            Demo Data
          </span>
        )}
      </div>

      {/* Channel Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {Object.entries(CHANNEL_COLORS).map(([channel, color]) => {
          const count = channelCounts[channel] ?? 0;
          return (
            <div key={channel} className="glass rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ background: color }}
                />
                <span className="text-sm font-medium capitalize">{channel.replace("_", " ")}</span>
              </div>
              <div className="text-2xl font-bold">{count}</div>
              <div className="text-xs text-[var(--text-muted)]">distributions sent</div>
            </div>
          );
        })}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-[var(--accent-cyan)]">{distributionLogs.length}</div>
          <div className="text-xs text-[var(--text-muted)]">Total Sends</div>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl font-bold">${totalCost.toFixed(2)}</div>
          <div className="text-xs text-[var(--text-muted)]">Total Cost</div>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl font-bold">
            ${distributionLogs.length > 0 ? (totalCost / distributionLogs.length).toFixed(3) : "0.00"}
          </div>
          <div className="text-xs text-[var(--text-muted)]">Avg Cost/Send</div>
        </div>
      </div>

      {/* Distribution Log */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-white/5">
          <h2 className="font-semibold">Distribution Log</h2>
        </div>
        <div className="divide-y divide-white/5">
          {distributionLogs.map((log) => {
            const channel = log.action.replace("distribute_", "");
            const parsed = parseDistributionOutput(log.output);
            return (
              <div key={log.id} className="px-5 py-4 hover:bg-white/[0.02] transition-colors">
                <div className="flex items-center gap-3 mb-2">
                  <div
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ background: CHANNEL_COLORS[channel] ?? "#666" }}
                  />
                  <span className="text-sm font-medium capitalize">{channel.replace("_", " ")}</span>
                  <span className="text-xs text-[var(--text-muted)]">
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                  {log.cost_usd !== null && log.cost_usd > 0 && (
                    <span className="text-xs text-[var(--text-muted)]">${log.cost_usd.toFixed(4)}</span>
                  )}
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-[var(--accent-emerald)]/10 text-[var(--accent-emerald)]">
                    {log.status}
                  </span>
                </div>
                {parsed && (
                  <div className="ml-5 text-xs text-[var(--text-secondary)]">
                    {parsed.headline && <span className="font-medium">&quot;{parsed.headline}&quot;</span>}
                    {parsed.post_url && (
                      <a
                        href={parsed.post_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 text-[var(--accent-cyan)] hover:underline"
                      >
                        View post
                      </a>
                    )}
                  </div>
                )}
                {log.input && (
                  <div className="ml-5 text-xs text-[var(--text-muted)]">{log.input}</div>
                )}
              </div>
            );
          })}
          {distributionLogs.length === 0 && (
            <div className="px-5 py-8 text-center text-[var(--text-muted)]">
              No distributions yet. Mercury distributes landing pages built by Forge.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
