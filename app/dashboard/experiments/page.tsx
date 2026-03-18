"use client";

import { useState, useEffect } from "react";
import type { AtlasExperiment } from "@/app/lib/atlas-types";
import { mockExperiments } from "@/app/lib/mock-data";

const STATUS_STYLES: Record<string, string> = {
  running: "bg-[var(--accent-emerald)]/10 text-[var(--accent-emerald)]",
  active: "bg-[var(--accent-blue)]/10 text-[var(--accent-blue)]",
  planned: "bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]",
  completed: "bg-[var(--accent-purple)]/10 text-[var(--accent-purple)]",
  failed: "bg-[var(--accent-rose)]/10 text-[var(--accent-rose)]",
  budget_denied: "bg-[var(--accent-rose)]/10 text-[var(--accent-rose)]",
};

export default function ExperimentsPage() {
  const [experiments, setExperiments] = useState<AtlasExperiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/atlas?resource=experiments");
        const json = await res.json();
        setExperiments(json.data ?? mockExperiments);
        setLive(json.live ?? false);
      } catch {
        setExperiments(mockExperiments);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--text-muted)]">Loading experiments...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Experiments</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            {experiments.length} experiments by Forge
          </p>
        </div>
        {!live && (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]">
            Demo Data
          </span>
        )}
      </div>

      {/* Experiment Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        {experiments.map((exp) => {
          const budgetPercent = exp.budget_spent > 0 ? (exp.budget_spent / 50) * 100 : 0;
          return (
            <div key={exp.id} className="glass rounded-xl p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold">{exp.name}</h3>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">ID: {exp.id}</p>
                </div>
                <span
                  className={`px-2 py-0.5 rounded-md text-xs font-medium ${
                    STATUS_STYLES[exp.status] ?? "bg-white/5 text-[var(--text-muted)]"
                  }`}
                >
                  {exp.status}
                </span>
              </div>

              {/* Budget bar */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-[var(--text-muted)]">Budget used</span>
                  <span className="text-xs font-medium">${exp.budget_spent.toFixed(2)} / $50.00</span>
                </div>
                <div className="w-full h-2 rounded-full bg-white/5 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[var(--accent-blue)] transition-all"
                    style={{ width: `${Math.min(budgetPercent, 100)}%` }}
                  />
                </div>
              </div>

              {/* Details */}
              <div className="space-y-2 text-xs">
                {exp.landing_page_url && (
                  <div className="flex items-center gap-2">
                    <span className="text-[var(--text-muted)]">Landing page:</span>
                    <a
                      href={exp.landing_page_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[var(--accent-cyan)] hover:underline truncate"
                    >
                      {exp.landing_page_url.replace("https://", "")}
                    </a>
                  </div>
                )}
                {exp.distribution_channels && exp.distribution_channels.length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-[var(--text-muted)]">Channels:</span>
                    <div className="flex gap-1">
                      {exp.distribution_channels.map((ch) => (
                        <span
                          key={ch}
                          className="px-1.5 py-0.5 rounded bg-white/5 text-[var(--text-secondary)] capitalize"
                        >
                          {ch}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {exp.started_at && (
                  <div className="flex items-center gap-2">
                    <span className="text-[var(--text-muted)]">Started:</span>
                    <span className="text-[var(--text-secondary)]">
                      {new Date(exp.started_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {experiments.length === 0 && (
        <div className="glass rounded-xl p-8 text-center">
          <p className="text-[var(--text-muted)]">No experiments yet. Forge will create landing pages when Scout finds high-scoring opportunities.</p>
        </div>
      )}
    </div>
  );
}
