"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import type {
  AtlasPipelineItem,
  PipelineStage,
  PendingApprovalItem,
} from "@/app/lib/atlas-types";
import { PIPELINE_STAGES } from "@/app/lib/atlas-types";
import { mockPipeline } from "@/app/lib/mock-data";

/* ─── Helper: safely parse JSON strings ─── */
function safeParse(raw: string | null | undefined): Record<string, unknown> {
  if (!raw) return {};
  try {
    return typeof raw === "object" ? raw : JSON.parse(raw);
  } catch {
    return {};
  }
}

/* ─── Pending Approval Card (extracted for readability) ─── */
function ApprovalCard({
  item,
  onApprove,
  onReject,
  actionInProgress,
}: {
  item: PendingApprovalItem;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  actionInProgress: string | null;
}) {
  const [expanded, setExpanded] = useState(false);
  const opp = item.atlas_opportunities;
  const proposal = item.proposals?.[0];
  const proposalContent = safeParse(proposal?.content ?? null);
  const pricing = safeParse(proposal?.pricing ?? null);
  const roi = safeParse(proposal?.roi_estimate ?? null);
  const notes = safeParse(item.notes);
  const isActing = actionInProgress === item.id;

  return (
    <div
      className="glass rounded-xl p-4 border border-[#f59e0b]/30"
      style={{ borderLeft: "4px solid #f59e0b" }}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold">
              {item.company_name || "Unknown Company"}
            </span>
            {opp?.sonnet_score != null && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[var(--accent-indigo)]/20 text-[var(--accent-indigo)]">
                Score: {opp.sonnet_score}
              </span>
            )}
          </div>
          <div className="text-xs text-[var(--text-muted)] mt-0.5">
            {opp?.target_vertical || "General"} &middot; {item.contact_name || "Unknown contact"}
          </div>
          {opp?.title && (
            <div className="text-xs text-[var(--text-secondary)] mt-1">
              {opp.title}
            </div>
          )}
        </div>

        <div className="text-right shrink-0">
          <div className="text-sm font-bold text-[var(--accent-emerald)]">
            ${(item.deal_value ?? 0).toLocaleString()} {item.currency || "AUD"}
          </div>
          <div className="text-[10px] text-[var(--text-muted)] mt-0.5">
            {new Date(item.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>

      {/* Source link */}
      {opp?.source_url && (
        <a
          href={opp.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-2 text-xs text-[var(--accent-cyan)] hover:underline truncate max-w-full"
        >
          View original post
        </a>
      )}

      {/* Quick notes */}
      {(notes.pain_point || notes.outreach_hook) && (
        <div className="mt-2 text-xs text-[var(--text-secondary)]">
          {notes.pain_point && (
            <div>
              <span className="font-medium text-[var(--text-primary)]">Pain: </span>
              {String(notes.pain_point)}
            </div>
          )}
          {notes.outreach_hook && (
            <div className="mt-0.5">
              <span className="font-medium text-[var(--text-primary)]">Hook: </span>
              {String(notes.outreach_hook)}
            </div>
          )}
        </div>
      )}

      {/* Expand/collapse proposal */}
      {proposal && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="mt-2 text-xs font-medium text-[var(--accent-amber)] hover:text-[var(--accent-amber)]/80 transition-colors"
        >
          {expanded ? "Hide proposal" : "Show proposal"}
        </button>
      )}

      {expanded && proposal && (
        <div className="mt-3 p-3 rounded-lg bg-[var(--surface-secondary)] text-xs space-y-2 max-h-96 overflow-y-auto">
          {proposalContent.executive_summary && (
            <div>
              <div className="font-semibold text-[var(--text-primary)] mb-0.5">
                Executive Summary
              </div>
              <div className="text-[var(--text-secondary)]">
                {String(proposalContent.executive_summary)}
              </div>
            </div>
          )}
          {proposalContent.problem_statement && (
            <div>
              <div className="font-semibold text-[var(--text-primary)] mb-0.5">
                Problem Statement
              </div>
              <div className="text-[var(--text-secondary)]">
                {String(proposalContent.problem_statement)}
              </div>
            </div>
          )}
          {proposalContent.proposed_solution && (
            <div>
              <div className="font-semibold text-[var(--text-primary)] mb-0.5">
                Proposed Solution
              </div>
              <div className="text-[var(--text-secondary)]">
                {String(proposalContent.proposed_solution)}
              </div>
            </div>
          )}
          {pricing.recommended && (
            <div>
              <div className="font-semibold text-[var(--text-primary)] mb-0.5">
                Recommended Tier
              </div>
              <div className="text-[var(--accent-emerald)] font-medium">
                {String(pricing.recommended).toUpperCase()}
                {pricing.justification && (
                  <span className="text-[var(--text-muted)] font-normal ml-1">
                    -- {String(pricing.justification)}
                  </span>
                )}
              </div>
            </div>
          )}
          {roi.monthly_savings_aud && (
            <div>
              <div className="font-semibold text-[var(--text-primary)] mb-0.5">
                ROI Estimate
              </div>
              <div className="text-[var(--text-secondary)]">
                Saves ${Number(roi.monthly_savings_aud).toLocaleString()}/mo
                {roi.payback_weeks && (
                  <span> &middot; Payback in {String(roi.payback_weeks)} weeks</span>
                )}
              </div>
            </div>
          )}
          {proposalContent.timeline && (
            <div>
              <div className="font-semibold text-[var(--text-primary)] mb-0.5">
                Timeline
              </div>
              <div className="text-[var(--text-secondary)]">
                {String(proposalContent.timeline)}
              </div>
            </div>
          )}
          {proposalContent.next_steps && (
            <div>
              <div className="font-semibold text-[var(--text-primary)] mb-0.5">
                Next Steps
              </div>
              <div className="text-[var(--text-secondary)]">
                {String(proposalContent.next_steps)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 mt-3">
        <button
          onClick={() => onApprove(item.id)}
          disabled={isActing}
          className="flex-1 px-3 py-2 rounded-lg text-xs font-semibold transition-all
            bg-[#22c55e]/20 text-[#22c55e] hover:bg-[#22c55e]/30
            disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isActing ? "Processing..." : "Approve & Send"}
        </button>
        <button
          onClick={() => onReject(item.id)}
          disabled={isActing}
          className="flex-1 px-3 py-2 rounded-lg text-xs font-semibold transition-all
            bg-[#ef4444]/20 text-[#ef4444] hover:bg-[#ef4444]/30
            disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isActing ? "Processing..." : "Reject"}
        </button>
      </div>
    </div>
  );
}

/* ─── Main Pipeline Page ─── */
export default function PipelinePage() {
  const [pipeline, setPipeline] = useState<AtlasPipelineItem[]>([]);
  const [pendingItems, setPendingItems] = useState<PendingApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [pipelineRes, pendingRes] = await Promise.all([
        fetch("/api/atlas?resource=pipeline"),
        fetch("/api/atlas?resource=pending"),
      ]);
      const pipelineJson = await pipelineRes.json();
      const pendingJson = await pendingRes.json();

      setPipeline(pipelineJson.data ?? mockPipeline);
      setLive(pipelineJson.live ?? false);

      const pendingData = pendingJson.data;
      if (pendingData && Array.isArray(pendingData.pending)) {
        setPendingItems(pendingData.pending);
      } else {
        setPendingItems([]);
      }
    } catch {
      setPipeline(mockPipeline);
      setPendingItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleApprove = useCallback(
    async (pipelineId: string) => {
      setActionInProgress(pipelineId);
      try {
        await fetch(
          `/api/atlas?resource=approve&id=${encodeURIComponent(pipelineId)}`,
          { method: "POST" }
        );
        await loadData();
      } catch {
        // Silently fail -- user can retry
      } finally {
        setActionInProgress(null);
      }
    },
    [loadData]
  );

  const handleReject = useCallback(
    async (pipelineId: string) => {
      setActionInProgress(pipelineId);
      try {
        await fetch(
          `/api/atlas?resource=reject&id=${encodeURIComponent(pipelineId)}`,
          { method: "POST" }
        );
        await loadData();
      } catch {
        // Silently fail -- user can retry
      } finally {
        setActionInProgress(null);
      }
    },
    [loadData]
  );

  const stageGroups = useMemo(() => {
    const groups: Record<PipelineStage, AtlasPipelineItem[]> = {
      discovered: [],
      qualified: [],
      pending_review: [],
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

      {/* ━━━ Pending Review Section ━━━ */}
      {pendingItems.length > 0 && (
        <div className="mb-6 rounded-xl border border-[#f59e0b]/40 bg-[#f59e0b]/5 p-4">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2.5 h-2.5 rounded-full bg-[#f59e0b] animate-pulse" />
            <h2 className="text-base font-bold text-[#f59e0b]">
              {pendingItems.length} proposal{pendingItems.length !== 1 ? "s" : ""} pending your review
            </h2>
          </div>
          <p className="text-xs text-[var(--text-muted)] mb-4">
            CLOSER generated these proposals. Review and approve before they are sent.
          </p>
          <div className="space-y-3">
            {pendingItems.map((item) => (
              <ApprovalCard
                key={item.id}
                item={item}
                onApprove={handleApprove}
                onReject={handleReject}
                actionInProgress={actionInProgress}
              />
            ))}
          </div>
        </div>
      )}

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
