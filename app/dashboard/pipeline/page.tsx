"use client";

import { useState, useEffect, useMemo } from "react";
import type { AtlasPipelineItem, PipelineStage } from "@/app/lib/atlas-types";
import { PIPELINE_STAGES } from "@/app/lib/atlas-types";
import { mockPipeline } from "@/app/lib/mock-data";

export default function PipelinePage() {
  const [pipeline, setPipeline] = useState<AtlasPipelineItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/atlas?resource=pipeline");
        const json = await res.json();
        setPipeline(json.data ?? mockPipeline);
        setLive(json.live ?? false);
      } catch {
        setPipeline(mockPipeline);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const stageGroups = useMemo(() => {
    const groups: Record<PipelineStage, AtlasPipelineItem[]> = {
      discovered: [],
      qualified: [],
      proposed: [],
      responded: [],
      closed: [],
      delivering: [],
    };
    for (const item of pipeline) {
      if (groups[item.stage]) {
        groups[item.stage].push(item);
      }
    }
    return groups;
  }, [pipeline]);

  const totalValue = useMemo(() => {
    return pipeline.reduce((sum, p) => sum + p.value, 0);
  }, [pipeline]);

  const closedValue = useMemo(() => {
    return pipeline
      .filter((p) => p.stage === "closed" || p.stage === "delivering")
      .reduce((sum, p) => sum + p.value, 0);
  }, [pipeline]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--text-muted)]">Loading pipeline...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Pipeline</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            Sales tracking -- {pipeline.length} deals
          </p>
        </div>
        {!live && (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]">
            Demo Data
          </span>
        )}
      </div>

      {/* Pipeline Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl font-bold">{pipeline.length}</div>
          <div className="text-xs text-[var(--text-muted)]">Total Deals</div>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl font-bold">${totalValue.toLocaleString()}</div>
          <div className="text-xs text-[var(--text-muted)]">Pipeline MRR</div>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-[var(--accent-emerald)]">${closedValue.toLocaleString()}</div>
          <div className="text-xs text-[var(--text-muted)]">Won MRR</div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-4 min-w-[900px]">
          {PIPELINE_STAGES.map((stage) => {
            const items = stageGroups[stage.key];
            const stageValue = items.reduce((sum, i) => sum + i.value, 0);

            return (
              <div key={stage.key} className="flex-1 min-w-[160px]">
                {/* Stage Header */}
                <div className="flex items-center justify-between mb-3 px-1">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ background: stage.color }}
                    />
                    <span className="text-xs font-semibold uppercase tracking-wider">
                      {stage.label}
                    </span>
                  </div>
                  <span className="text-xs text-[var(--text-muted)]">{items.length}</span>
                </div>

                {/* Stage Value */}
                {stageValue > 0 && (
                  <div className="text-xs text-[var(--text-muted)] mb-2 px-1">
                    ${stageValue.toLocaleString()}/mo
                  </div>
                )}

                {/* Cards */}
                <div className="space-y-2">
                  {items.map((item) => (
                    <div
                      key={item.id}
                      className="glass rounded-lg p-3 hover-lift"
                      style={{ borderLeft: `3px solid ${stage.color}` }}
                    >
                      <div className="text-sm font-medium mb-1">{item.title}</div>
                      <div className="text-xs text-[var(--text-muted)] mb-2">{item.vertical}</div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-[var(--accent-emerald)]">
                          ${item.value}/mo
                        </span>
                        {item.contact && (
                          <span className="text-[var(--text-muted)] truncate ml-2">
                            {item.contact}
                          </span>
                        )}
                      </div>
                      {item.notes && (
                        <div className="text-[10px] text-[var(--text-muted)] mt-1.5 line-clamp-2">
                          {item.notes}
                        </div>
                      )}
                    </div>
                  ))}
                  {items.length === 0 && (
                    <div className="glass rounded-lg p-3 text-center">
                      <span className="text-xs text-[var(--text-muted)]">Empty</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
