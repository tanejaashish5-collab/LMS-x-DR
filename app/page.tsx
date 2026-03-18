"use client";

import { useState, useMemo } from "react";

/* ─── Service Verticals from ATLAS ─── */
const services = [
  {
    id: 1,
    name: "Review Autopilot",
    icon: "⭐",
    tagline: "5-star reviews on autopilot for local businesses",
    description: "Automated review collection, sentiment analysis, and response management system that turns happy customers into 5-star advocates.",
    features: ["SMS & Email Campaigns", "AI Response Generation", "Multi-platform Integration", "Sentiment Analysis"],
    roi: "300% increase in reviews",
    price: "$497/mo",
    color: "#6366f1"
  },
  {
    id: 2,
    name: "Client Intake Automation",
    icon: "📋",
    tagline: "Convert inquiries to clients while you sleep",
    description: "Intelligent form processing, qualification scoring, and automated follow-up that turns website visitors into booked appointments.",
    features: ["Smart Qualification", "Calendar Integration", "Document Collection", "Automated Nurturing"],
    roi: "8 hours saved weekly",
    price: "$397/mo",
    color: "#8b5cf6"
  },
  {
    id: 3,
    name: "AR Collections AI",
    icon: "💰",
    tagline: "Get paid faster with empathetic AI",
    description: "Diplomatic payment collection system that recovers overdue invoices while maintaining customer relationships.",
    features: ["Personalized Outreach", "Payment Plans", "Dispute Resolution", "Cash Flow Analytics"],
    roi: "42% faster collection",
    price: "$597/mo",
    color: "#10b981"
  },
  {
    id: 4,
    name: "Home Services Dispatcher",
    icon: "🏠",
    tagline: "Route optimization for service professionals",
    description: "Smart scheduling and routing system that maximizes daily appointments and minimizes drive time for field teams.",
    features: ["GPS Routing", "Job Batching", "Customer Notifications", "Technician Tracking"],
    roi: "+3 jobs per day",
    price: "$297/mo",
    color: "#f59e0b"
  },
  {
    id: 5,
    name: "AI Bookkeeping Assistant",
    icon: "📊",
    tagline: "Categorization and reconciliation on autopilot",
    description: "Intelligent transaction categorization and bank reconciliation that keeps your books perfect without the manual work.",
    features: ["Auto-categorization", "Receipt Scanning", "Bank Sync", "Tax Preparation"],
    roi: "15 hours saved monthly",
    price: "$197/mo",
    color: "#ef4444"
  },
  {
    id: 6,
    name: "Legal Document Processor",
    icon: "⚖️",
    tagline: "Paralegal-level document automation",
    description: "Extract key terms, populate templates, and manage document workflows with legal-grade accuracy and compliance.",
    features: ["Contract Analysis", "Template Library", "Deadline Tracking", "E-signature Integration"],
    roi: "$50K paralegal replaced",
    price: "$797/mo",
    color: "#06b6d4"
  },
  {
    id: 7,
    name: "Healthcare Intake Flow",
    icon: "🏥",
    tagline: "HIPAA-compliant patient onboarding",
    description: "Secure patient intake system with insurance verification, consent management, and appointment scheduling.",
    features: ["Insurance Verification", "Digital Forms", "Consent Management", "Patient Portal"],
    roi: "70% less admin work",
    price: "$697/mo",
    color: "#ec4899"
  },
  {
    id: 8,
    name: "Real Estate Lead Nurture",
    icon: "🏘️",
    tagline: "Turn Zillow leads into closed deals",
    description: "Multi-channel lead nurturing system that maintains engagement until prospects are ready to buy or sell.",
    features: ["Drip Campaigns", "Property Alerts", "CMA Automation", "Showing Scheduler"],
    roi: "2x conversion rate",
    price: "$497/mo",
    color: "#84cc16"
  },
  {
    id: 9,
    name: "E-commerce Operations",
    icon: "🛒",
    tagline: "Inventory, orders, and customer service unified",
    description: "Unified operations platform that manages inventory, processes orders, and handles customer service across all channels.",
    features: ["Multi-channel Sync", "Inventory Alerts", "Order Routing", "Returns Processing"],
    roi: "30% operational savings",
    price: "$397/mo",
    color: "#a855f7"
  },
  {
    id: 10,
    name: "SaaS User Onboarding",
    icon: "🚀",
    tagline: "Convert trials to paid in 14 days",
    description: "Behavioral-triggered onboarding sequences that guide trial users to their 'aha moment' and convert them to paying customers.",
    features: ["Usage Analytics", "Milestone Tracking", "In-app Messaging", "Churn Prediction"],
    roi: "25% trial conversion",
    price: "$297/mo",
    color: "#3b82f6"
  },
  {
    id: 11,
    name: "Restaurant Operations Hub",
    icon: "🍽️",
    tagline: "Orders, inventory, and staffing simplified",
    description: "Integrated system managing online orders, inventory tracking, and staff scheduling for modern restaurants.",
    features: ["Multi-platform Orders", "Inventory Tracking", "Staff Scheduling", "Customer Analytics"],
    roi: "20% food cost reduction",
    price: "$597/mo",
    color: "#f97316"
  },
  {
    id: 12,
    name: "Education Admin Suite",
    icon: "🎓",
    tagline: "Enrollment to graduation automation",
    description: "Complete student lifecycle management from application processing to alumni engagement.",
    features: ["Application Processing", "Course Registration", "Grade Management", "Alumni Tracking"],
    roi: "80% admin reduction",
    price: "$897/mo",
    color: "#0ea5e9"
  }
];

/* ─── Stats Component ─── */
function Stats() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-12 mb-20">
      <div className="glass rounded-2xl p-6 text-center hover-lift">
        <div className="text-3xl font-bold gradient-text">12</div>
        <div className="text-sm text-[var(--text-secondary)] mt-1">Industry Solutions</div>
      </div>
      <div className="glass rounded-2xl p-6 text-center hover-lift">
        <div className="text-3xl font-bold gradient-text">48hrs</div>
        <div className="text-sm text-[var(--text-secondary)] mt-1">Setup Time</div>
      </div>
      <div className="glass rounded-2xl p-6 text-center hover-lift">
        <div className="text-3xl font-bold gradient-text">300%</div>
        <div className="text-sm text-[var(--text-secondary)] mt-1">Average ROI</div>
      </div>
      <div className="glass rounded-2xl p-6 text-center hover-lift">
        <div className="text-3xl font-bold gradient-text">24/7</div>
        <div className="text-sm text-[var(--text-secondary)] mt-1">AI Operation</div>
      </div>
    </div>
  );
}

/* ─── Service Card ─── */
function ServiceCard({ service, isExpanded, onToggle }: { service: any; isExpanded: boolean; onToggle: () => void }) {
  return (
    <div className={`glass rounded-2xl overflow-hidden hover-lift transition-all duration-300 ${
      isExpanded ? "ring-2 ring-[var(--accent-blue)]/30" : ""
    }`}>
      <button
        onClick={onToggle}
        className="w-full text-left p-6 cursor-pointer"
      >
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
            style={{ background: `${service.color}20`, color: service.color }}
          >
            {service.icon}
          </div>

          {/* Content */}
          <div className="flex-1">
            <h3 className="font-semibold text-lg text-[var(--text-primary)] mb-1">
              {service.name}
            </h3>
            <p className="text-sm text-[var(--text-secondary)] mb-3">
              {service.tagline}
            </p>
            <div className="flex items-center gap-4 text-sm">
              <span className="font-semibold" style={{ color: service.color }}>
                {service.price}
              </span>
              <span className="text-[var(--text-muted)]">•</span>
              <span className="text-[var(--accent-emerald)] font-medium">
                {service.roi}
              </span>
            </div>
          </div>

          {/* Chevron */}
          <svg
            className={`w-5 h-5 text-[var(--text-muted)] transition-transform shrink-0 mt-1 ${
              isExpanded ? "rotate-180" : ""
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="px-6 pb-6 border-t border-white/5 animate-fade-in">
          <p className="text-sm text-[var(--text-secondary)] mt-4 mb-4 leading-relaxed">
            {service.description}
          </p>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="rounded-xl bg-white/5 p-4">
              <h4 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3">
                Key Features
              </h4>
              <ul className="space-y-2">
                {service.features.map((feature: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-[var(--accent-cyan)] mt-0.5">✓</span>
                    <span className="text-[var(--text-primary)]">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-xl bg-gradient-to-br from-[var(--accent-blue)]/10 to-[var(--accent-purple)]/10 border border-[var(--accent-blue)]/20 p-4">
              <h4 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3">
                Implementation
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-[var(--accent-blue)]">⚡</span>
                  <span className="text-[var(--text-primary)]">48-hour setup</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[var(--accent-purple)]">🤖</span>
                  <span className="text-[var(--text-primary)]">Fully autonomous</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[var(--accent-cyan)]">📊</span>
                  <span className="text-[var(--text-primary)]">Real-time analytics</span>
                </div>
              </div>
            </div>
          </div>

          <button className="mt-4 w-full py-3 rounded-xl bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] text-white font-semibold hover:shadow-lg hover:shadow-[var(--accent-blue)]/20 transition-all">
            Start Free 14-Day Trial
          </button>
        </div>
      )}
    </div>
  );
}

/* ─── How It Works ─── */
function HowItWorks() {
  const steps = [
    { icon: "🔍", title: "Discovery Call", desc: "15-min assessment of your workflow bottlenecks" },
    { icon: "🏗️", title: "Custom Build", desc: "48-hour implementation by our AI architects" },
    { icon: "🚀", title: "Go Live", desc: "Launch with full training and documentation" },
    { icon: "📈", title: "Scale", desc: "Continuous optimization based on performance" }
  ];

  return (
    <section className="max-w-6xl mx-auto px-5 py-20">
      <h2 className="text-2xl font-bold text-center mb-12">
        How ForgeVoice Works
      </h2>
      <div className="grid md:grid-cols-4 gap-6">
        {steps.map((step, i) => (
          <div key={i} className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-[var(--accent-blue)]/20 to-[var(--accent-purple)]/20 flex items-center justify-center text-2xl">
              {step.icon}
            </div>
            <h3 className="font-semibold mb-2">{step.title}</h3>
            <p className="text-sm text-[var(--text-secondary)]">{step.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ─── Main Page ─── */
export default function Home() {
  const [openId, setOpenId] = useState<number | null>(null);
  const [filter, setFilter] = useState("all");

  const filteredServices = useMemo(() => {
    if (filter === "all") return services;
    if (filter === "professional") return services.filter(s => [2, 6, 7].includes(s.id));
    if (filter === "retail") return services.filter(s => [1, 4, 9, 11].includes(s.id));
    if (filter === "b2b") return services.filter(s => [3, 5, 8, 10, 12].includes(s.id));
    return services;
  }, [filter]);

  return (
    <>
      {/* Background */}
      <div className="bg-mesh" />

      <div className="relative z-10">
        {/* Header */}
        <header className="max-w-6xl mx-auto px-5 pt-8">
          <nav className="flex items-center justify-between mb-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] flex items-center justify-center">
                <span className="text-white text-lg font-black">F</span>
              </div>
              <span className="font-bold text-lg">ForgeVoice Studio</span>
            </div>
            <div className="flex items-center gap-6 text-sm">
              <a href="#services" className="hover:text-[var(--accent-blue)] transition-colors">
                Solutions
              </a>
              <a href="#how" className="hover:text-[var(--accent-blue)] transition-colors">
                Process
              </a>
              <a href="/dashboard"
                 className="px-4 py-2 rounded-xl bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] text-white font-medium hover:shadow-lg hover:shadow-[var(--accent-blue)]/20 transition-all">
                Dashboard
              </a>
            </div>
          </nav>

          {/* Hero */}
          <div className="py-16">
            <div className="max-w-4xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs font-medium text-[var(--accent-cyan)] mb-6">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-cyan)] animate-pulse" />
                Powered by ATLAS Agent Swarm™
              </div>

              <h1 className="text-5xl lg:text-7xl font-black leading-tight tracking-tight mb-6">
                AI Automation
                <br />
                <span className="gradient-text">Built in 48 Hours</span>
              </h1>

              <p className="text-xl text-[var(--text-secondary)] max-w-2xl mx-auto leading-relaxed mb-8">
                Stop losing money to manual workflows. We build intelligent automation
                that runs your business operations 24/7, starting at $197/month.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="px-8 py-4 rounded-xl bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] text-white font-semibold hover:shadow-xl hover:shadow-[var(--accent-blue)]/20 transition-all text-lg">
                  Book Free Strategy Call
                </button>
                <button className="px-8 py-4 rounded-xl glass font-semibold hover:bg-white/10 transition-all text-lg">
                  Watch 2-Min Demo
                </button>
              </div>
            </div>

            <Stats />
          </div>
        </header>

        {/* Services */}
        <section id="services" className="max-w-6xl mx-auto px-5 pb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">
              Industry-Specific Solutions
            </h2>
            <p className="text-[var(--text-secondary)] max-w-2xl mx-auto">
              Pre-built automation frameworks customized for your industry's unique workflows.
              Every solution is battle-tested and delivering ROI today.
            </p>
          </div>

          {/* Filter Tabs */}
          <div className="flex justify-center gap-2 mb-8">
            {[
              { key: "all", label: "All Industries" },
              { key: "professional", label: "Professional Services" },
              { key: "retail", label: "Retail & Local" },
              { key: "b2b", label: "B2B & SaaS" }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  filter === tab.key
                    ? "bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] text-white shadow-lg shadow-[var(--accent-blue)]/20"
                    : "glass text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Service Grid */}
          <div className="grid lg:grid-cols-2 gap-4">
            {filteredServices.map(service => (
              <ServiceCard
                key={service.id}
                service={service}
                isExpanded={openId === service.id}
                onToggle={() => setOpenId(openId === service.id ? null : service.id)}
              />
            ))}
          </div>
        </section>

        {/* How It Works */}
        <div id="how">
          <HowItWorks />
        </div>

        {/* CTA Section */}
        <section className="max-w-6xl mx-auto px-5 pb-20">
          <div className="glass rounded-3xl p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">
              Your Competition is Automating. Are You?
            </h2>
            <p className="text-lg text-[var(--text-secondary)] max-w-2xl mx-auto mb-8">
              Every day you wait costs you money. Book a free 15-minute strategy call
              to see your custom automation roadmap.
            </p>
            <button className="px-8 py-4 rounded-xl bg-gradient-to-r from-[var(--accent-blue)] to-[var(--accent-purple)] text-white font-semibold hover:shadow-xl hover:shadow-[var(--accent-blue)]/20 transition-all text-lg">
              Claim Your Free Automation Audit →
            </button>
            <p className="text-sm text-[var(--text-muted)] mt-4">
              No credit card required • Results in 48 hours • Cancel anytime
            </p>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 py-8">
          <div className="max-w-6xl mx-auto px-5">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] flex items-center justify-center">
                  <span className="text-white text-sm font-black">F</span>
                </div>
                <span className="text-sm text-[var(--text-muted)]">
                  ForgeVoice Studio — AI Automation That Actually Works™
                </span>
              </div>
              <div className="flex gap-6 text-sm text-[var(--text-muted)]">
                <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Terms</a>
                <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Privacy</a>
                <a href="mailto:hello@forgevoice.studio" className="hover:text-[var(--text-primary)] transition-colors">
                  hello@forgevoice.studio
                </a>
              </div>
            </div>
            <div className="text-center text-xs text-[var(--text-muted)] mt-6">
              Powered by ATLAS Agent Swarm™ — 6 AI agents working 24/7 to grow your business
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}