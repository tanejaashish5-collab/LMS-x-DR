"use client";

import { useState, useEffect, useMemo } from "react";
import type { AtlasOpportunity } from "@/app/lib/atlas-types";
import { mockOpportunities } from "@/app/lib/mock-data";

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-[var(--text-muted)]">--</span>;
  const color =
    score >= 80
      ? "bg-[var(--accent-emerald)]/10 text-[var(--accent-emerald)]"
      : score >= 60
      ? "bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]"
      : "bg-[var(--accent-rose)]/10 text-[var(--accent-rose)]";
  return (
    <span className={`px-2 py-0.5 rounded-md text-xs font-bold ${color}`}>
      {score}
    </span>
  );
}

type SortKey = "sonnet_score" | "discovered_at" | "title";

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<AtlasOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("sonnet_score");
  const [filterCategory, setFilterCategory] = useState("all");
  const [filterVertical, setFilterVertical] = useState("all");

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/atlas?resource=opportunities");
        const json = await res.json();
        setOpportunities(json.data ?? mockOpportunities);
        setLive(json.live ?? false);
      } catch {
        setOpportunities(mockOpportunities);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const categories = useMemo(() => {
    const cats = new Set(opportunities.map((o) => o.category));
    return Array.from(cats).sort();
  }, [opportunities]);

  const verticals = useMemo(() => {
    const verts = new Set(
      opportunities.map((o) => o.target_vertical).filter(Boolean) as string[]
    );
    return Array.from(verts).sort();
  }, [opportunities]);

  const filtered = useMemo(() => {
    let result = [...opportunities];

    if (filterCategory !== "all") {
      result = result.filter((o) => o.category === filterCategory);
    }
    if (filterVertical !== "all") {
      result = result.filter((o) => o.target_vertical === filterVertical);
    }

    result.sort((a, b) => {
      if (sortKey === "sonnet_score") {
        return (b.sonnet_score ?? 0) - (a.sonnet_score ?? 0);
      }
      if (sortKey === "discovered_at") {
        return new Date(b.discovered_at).getTime() - new Date(a.discovered_at).getTime();
      }
      return a.title.localeCompare(b.title);
    });

    return result;
  }, [opportunities, sortKey, filterCategory, filterVertical]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--text-muted)]">Loading opportunities...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Opportunities</h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            {filtered.length} opportunities scored by Scout
          </p>
        </div>
        {!live && (
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-amber)]/10 text-[var(--accent-amber)]">
            Demo Data
          </span>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={sortKey}
          onChange={(e) => setSortKey(e.target.value as SortKey)}
          className="glass rounded-lg px-3 py-2 text-sm bg-transparent text-[var(--text-primary)] border-0 outline-none cursor-pointer"
        >
          <option value="sonnet_score">Sort: Score</option>
          <option value="discovered_at">Sort: Newest</option>
          <option value="title">Sort: A-Z</option>
        </select>

        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="glass rounded-lg px-3 py-2 text-sm bg-transparent text-[var(--text-primary)] border-0 outline-none cursor-pointer"
        >
          <option value="all">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c.replace(/_/g, " ")}
            </option>
          ))}
        </select>

        <select
          value={filterVertical}
          onChange={(e) => setFilterVertical(e.target.value)}
          className="glass rounded-lg px-3 py-2 text-sm bg-transparent text-[var(--text-primary)] border-0 outline-none cursor-pointer"
        >
          <option value="all">All Verticals</option>
          {verticals.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium">Title</th>
                <th className="text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium hidden md:table-cell">Vertical</th>
                <th className="text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium hidden lg:table-cell">Category</th>
                <th className="text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium hidden lg:table-cell">Source</th>
                <th className="text-center px-4 py-3 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium">Score</th>
                <th className="text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase tracking-wider font-medium hidden md:table-cell">Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((opp) => (
                <tr
                  key={opp.id}
                  className="border-b border-white/5 hover:bg-white/[0.02] transition-colors"
                >
                  <td className="px-4 py-3">
                    <div className="font-medium">{opp.title}</div>
                    <div className="text-xs text-[var(--text-muted)] mt-0.5 md:hidden">
                      {opp.target_vertical ?? "--"}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-[var(--text-secondary)] hidden md:table-cell">
                    {opp.target_vertical ?? "--"}
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell">
                    <span className="px-2 py-0.5 rounded-md text-xs bg-white/5 text-[var(--text-secondary)]">
                      {opp.category.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[var(--text-secondary)] hidden lg:table-cell capitalize">
                    {opp.source}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <ScoreBadge score={opp.sonnet_score} />
                  </td>
                  <td className="px-4 py-3 text-[var(--text-muted)] text-xs hidden md:table-cell">
                    {new Date(opp.discovered_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <div className="text-center py-8 text-[var(--text-muted)]">No opportunities match filters</div>
        )}
      </div>
    </div>
  );
}
