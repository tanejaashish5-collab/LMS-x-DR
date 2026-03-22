import { NextResponse } from "next/server";
import {
  getDashboardStats,
  getOpportunities,
  getBudgetSummary,
  getBudgetLedger,
  getExperiments,
  getAgentLogs,
  getPipeline,
  getPendingApprovals,
  isLive,
} from "@/app/lib/atlas-data";

function getAtlasApiUrl(): string {
  const url = process.env.ATLAS_API_URL;
  if (!url) {
    throw new Error("ATLAS_API_URL environment variable is not set");
  }
  return url;
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const resource = searchParams.get("resource") ?? "stats";

  try {
    let data: unknown;

    switch (resource) {
      case "stats":
        data = await getDashboardStats();
        break;
      case "opportunities":
        data = await getOpportunities();
        break;
      case "budget":
        data = {
          summary: await getBudgetSummary(),
          ledger: await getBudgetLedger(),
        };
        break;
      case "experiments":
        data = await getExperiments();
        break;
      case "logs":
        data = await getAgentLogs(100);
        break;
      case "pipeline":
        data = await getPipeline();
        break;
      case "pending":
        data = await getPendingApprovals();
        break;
      default:
        return NextResponse.json(
          { error: `Unknown resource: ${resource}` },
          { status: 400 }
        );
    }

    return NextResponse.json({ data, live: isLive() });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  const { searchParams } = new URL(request.url);
  const resource = searchParams.get("resource");
  const id = searchParams.get("id");

  try {
    const baseUrl = getAtlasApiUrl();

    if (resource === "approve" && id) {
      const res = await fetch(`${baseUrl}/api/pipeline/${id}/approve`, {
        method: "POST",
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        return NextResponse.json(
          { error: err.detail || "Approval failed" },
          { status: res.status }
        );
      }
      const data = await res.json();
      return NextResponse.json(data);
    }

    if (resource === "reject" && id) {
      const res = await fetch(`${baseUrl}/api/pipeline/${id}/reject`, {
        method: "POST",
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        return NextResponse.json(
          { error: err.detail || "Rejection failed" },
          { status: res.status }
        );
      }
      const data = await res.json();
      return NextResponse.json(data);
    }

    return NextResponse.json({ error: "Unknown action" }, { status: 400 });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
