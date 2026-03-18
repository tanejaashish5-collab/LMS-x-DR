import { NextResponse } from "next/server";
import {
  getDashboardStats,
  getOpportunities,
  getBudgetSummary,
  getBudgetLedger,
  getExperiments,
  getAgentLogs,
  getPipeline,
  isLive,
} from "@/app/lib/atlas-data";

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
