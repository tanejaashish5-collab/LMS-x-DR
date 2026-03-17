export interface Opportunity {
  id: number;
  name: string;
  shortName: string;
  icon: string;
  tagline: string;
  scores: {
    revenue: number;        // 1-10: Revenue potential
    marketSize: number;     // 1-10: TAM size
    easeOfBuild: number;    // 1-10: How easy to build (10=easiest)
    complexity: number;     // 1-10: Low complexity is better (10=simplest)
    replication: number;    // 1-10: Hard to replicate (10=hardest moat)
    competition: number;    // 1-10: Low competition (10=least competitive)
    marketGap: number;      // 1-10: Size of gap between need and solution
    autonomy: number;       // 1-10: How autonomous can it run (10=fully)
  };
  tam: string;
  monthlyPotential: string;
  timeToRevenue: string;
  roi: string;
  keyInsight: string;
  color: string;
}

export const opportunities: Opportunity[] = [
  {
    id: 1,
    name: "AI Accounts Receivable & Invoice Collections",
    shortName: "AR Collections",
    icon: "💰",
    tagline: "The diplomatic AI that handles the most uncomfortable part of business",
    scores: {
      revenue: 8,
      marketSize: 7,
      easeOfBuild: 8,
      complexity: 8,
      replication: 7,
      competition: 7,
      marketGap: 9,
      autonomy: 9,
    },
    tam: "$4.7B",
    monthlyPotential: "$30K-300K",
    timeToRevenue: "3-6 months",
    roi: "263-804x",
    keyInsight: "60% of founders avoid confronting customers about late bills. $39K/yr avg loss per SMB.",
    color: "#10B981",
  },
  {
    id: 2,
    name: "Healthcare Claims AI",
    shortName: "Healthcare Claims",
    icon: "🏥",
    tagline: "Fight AI-powered denials with AI-powered appeals",
    scores: {
      revenue: 10,
      marketSize: 10,
      easeOfBuild: 4,
      complexity: 3,
      replication: 8,
      competition: 6,
      marketGap: 9,
      autonomy: 7,
    },
    tam: "$262B problem",
    monthlyPotential: "$100K-1M",
    timeToRevenue: "6-12 months",
    roi: "30-125x",
    keyInsight: "Insurers use AI to deny 300K+ claims in 2 months. 86% of providers fight manually.",
    color: "#3B82F6",
  },
  {
    id: 3,
    name: "AI Home Services Operations",
    shortName: "Home Services",
    icon: "🔧",
    tagline: "Voice-driven AI for contractors who can't type while under a house",
    scores: {
      revenue: 9,
      marketSize: 10,
      easeOfBuild: 6,
      complexity: 5,
      replication: 7,
      competition: 8,
      marketGap: 10,
      autonomy: 8,
    },
    tam: "$750B",
    monthlyPotential: "$50K-500K",
    timeToRevenue: "3-6 months",
    roi: "50-100x",
    keyInsight: "ServiceTitan excludes <3 technician companies. 5-8 hrs/week wasted on quoting alone.",
    color: "#F59E0B",
  },
  {
    id: 4,
    name: "AI Legal Practice Operations",
    shortName: "Legal Ops",
    icon: "⚖️",
    tagline: "116-day billing cycles destroyed by AI",
    scores: {
      revenue: 8,
      marketSize: 9,
      easeOfBuild: 5,
      complexity: 4,
      replication: 7,
      competition: 5,
      marketGap: 8,
      autonomy: 7,
    },
    tam: "$350B",
    monthlyPotential: "$50K-300K",
    timeToRevenue: "4-8 months",
    roi: "31K/yr/atty",
    keyInsight: "600K+ solo/small lawyers priced out of Harvey AI ($1,200+/mo). 25% of malpractice = missed deadlines.",
    color: "#8B5CF6",
  },
  {
    id: 5,
    name: "AI Bookkeeping Autopilot",
    shortName: "Bookkeeping",
    icon: "📊",
    tagline: "QuickBooks has 1.1 stars. Bench collapsed. 5M new businesses need help.",
    scores: {
      revenue: 8,
      marketSize: 8,
      easeOfBuild: 6,
      complexity: 5,
      replication: 5,
      competition: 4,
      marketGap: 8,
      autonomy: 9,
    },
    tam: "$22B",
    monthlyPotential: "$50K-500K",
    timeToRevenue: "4-8 months",
    roi: "10-20x",
    keyInsight: "300K accountants left. 75% of CPAs retiring. QuickBooks forcing migrations with 400% price hikes.",
    color: "#EC4899",
  },
  {
    id: 6,
    name: "AI Client Intake Automation",
    shortName: "Client Intake",
    icon: "📋",
    tagline: "12-15 hours per client → 40 minutes. 526% documented ROI.",
    scores: {
      revenue: 6,
      marketSize: 5,
      easeOfBuild: 9,
      complexity: 8,
      replication: 5,
      competition: 7,
      marketGap: 8,
      autonomy: 9,
    },
    tam: "$2-5B",
    monthlyPotential: "$30K-150K",
    timeToRevenue: "3-6 months",
    roi: "526%",
    keyInsight: "503K firms waste 12-15 hrs/client. Solo firms see 53% higher revenue with automation.",
    color: "#14B8A6",
  },
  {
    id: 7,
    name: "AI Restaurant Operations",
    shortName: "Restaurant Ops",
    icon: "🍽️",
    tagline: "$162B in food waste. 58% track nothing. AI doubles profit.",
    scores: {
      revenue: 7,
      marketSize: 10,
      easeOfBuild: 5,
      complexity: 4,
      replication: 6,
      competition: 6,
      marketGap: 8,
      autonomy: 7,
    },
    tam: "$1.6T industry",
    monthlyPotential: "$50K-300K",
    timeToRevenue: "6-12 months",
    roi: "50-100x",
    keyInsight: "A $1M restaurant at 3% margin = $30K profit. Cutting waste from 8% to 4% = $40K saved.",
    color: "#F97316",
  },
  {
    id: 8,
    name: "Small Manufacturer Compliance AI",
    shortName: "Mfg Compliance",
    icon: "🏭",
    tagline: "$50K/employee/year burden. Avalara-scale exit opportunity.",
    scores: {
      revenue: 7,
      marketSize: 8,
      easeOfBuild: 4,
      complexity: 3,
      replication: 8,
      competition: 9,
      marketGap: 9,
      autonomy: 7,
    },
    tam: "$36.2B",
    monthlyPotential: "$30K-150K",
    timeToRevenue: "6-12 months",
    roi: "100x",
    keyInsight: "Small manufacturers pay 2x more per employee for compliance. SAP/Oracle = $100K+/yr. Gap is enormous.",
    color: "#6366F1",
  },
  {
    id: 9,
    name: "Boomer Knowledge Capture AI",
    shortName: "Knowledge Capture",
    icon: "🧠",
    tagline: "75M retiring. 46.7% CAGR. Passive knowledge extraction.",
    scores: {
      revenue: 7,
      marketSize: 7,
      easeOfBuild: 6,
      complexity: 5,
      replication: 7,
      competition: 8,
      marketGap: 9,
      autonomy: 6,
    },
    tam: "$51B by 2030",
    monthlyPotential: "$30K-100K",
    timeToRevenue: "4-8 months",
    roi: "GDP impact",
    keyInsight: "11,000 people/day hitting retirement. Boeing quality crisis traced to lost process knowledge.",
    color: "#A855F7",
  },
  {
    id: 10,
    name: "AI Reputation & Review Autopilot",
    shortName: "Review Autopilot",
    icon: "⭐",
    tagline: "88% of consumers choose businesses that respond to all reviews",
    scores: {
      revenue: 6,
      marketSize: 7,
      easeOfBuild: 9,
      complexity: 8,
      replication: 4,
      competition: 5,
      marketGap: 7,
      autonomy: 10,
    },
    tam: "$6.9B",
    monthlyPotential: "$20K-100K",
    timeToRevenue: "2-4 months",
    roi: "5-9% rev increase",
    keyInsight: "62.6% of SMBs manage reviews manually. 1-star increase = 5-9% revenue boost (Harvard).",
    color: "#EAB308",
  },
  {
    id: 11,
    name: "Cross-Border Trade Compliance",
    shortName: "Trade Compliance",
    icon: "🌍",
    tagline: "20% of sellers exiting. Tariff chaos. No SMB solution.",
    scores: {
      revenue: 7,
      marketSize: 6,
      easeOfBuild: 4,
      complexity: 3,
      replication: 8,
      competition: 9,
      marketGap: 9,
      autonomy: 6,
    },
    tam: "$1.5B",
    monthlyPotential: "$20K-100K",
    timeToRevenue: "6-12 months",
    roi: "Avoid $365K fines",
    keyInsight: "25-30% tariffs, most volatile in 40 years. Penalties up to $364,992/violation.",
    color: "#0EA5E9",
  },
  {
    id: 12,
    name: "AI Automation Agency (Service)",
    shortName: "AI Agency",
    icon: "🚀",
    tagline: "YC's #1 rec for 2026. $32K-80K MRR in weeks, not months.",
    scores: {
      revenue: 7,
      marketSize: 8,
      easeOfBuild: 10,
      complexity: 9,
      replication: 3,
      competition: 3,
      marketGap: 6,
      autonomy: 5,
    },
    tam: "Service model",
    monthlyPotential: "$32K-80K",
    timeToRevenue: "2-4 weeks",
    roi: "16-64x markup",
    keyInsight: "API cost $50-200/client. Charge $3,200/mo. 90% of AI startups fail building wrappers — agency doesn't.",
    color: "#EF4444",
  },
];

export const scoreLabels: Record<keyof Opportunity["scores"], string> = {
  revenue: "Revenue Potential",
  marketSize: "Market Size",
  easeOfBuild: "Ease of Build",
  complexity: "Low Complexity",
  replication: "Hard to Copy",
  competition: "Low Competition",
  marketGap: "Market Gap",
  autonomy: "Fully Autonomous",
};

export const scoreWeights: Record<keyof Opportunity["scores"], number> = {
  revenue: 1.5,
  marketSize: 1.2,
  easeOfBuild: 1.3,
  complexity: 1.0,
  replication: 1.1,
  competition: 1.2,
  marketGap: 1.4,
  autonomy: 1.3,
};

export function calculateWeightedScore(
  scores: Opportunity["scores"],
  weights: Record<keyof Opportunity["scores"], number> = scoreWeights
): number {
  const keys = Object.keys(scores) as (keyof Opportunity["scores"])[];
  const totalWeight = keys.reduce((sum, k) => sum + weights[k], 0);
  const weightedSum = keys.reduce(
    (sum, k) => sum + scores[k] * weights[k],
    0
  );
  return Math.round((weightedSum / totalWeight) * 10) / 10;
}
