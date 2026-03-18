"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: "O" },
  { href: "/dashboard/opportunities", label: "Opportunities", icon: "S" },
  { href: "/dashboard/budget", label: "Budget", icon: "V" },
  { href: "/dashboard/experiments", label: "Experiments", icon: "F" },
  { href: "/dashboard/distribution", label: "Distribution", icon: "M" },
  { href: "/dashboard/pipeline", label: "Pipeline", icon: "P" },
  { href: "/dashboard/agents", label: "Agent Logs", icon: "L" },
];

function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-56 shrink-0 border-r border-white/5 bg-[var(--bg-secondary)] min-h-screen">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3 px-5 py-5 border-b border-white/5">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] flex items-center justify-center">
          <span className="text-white text-sm font-black">A</span>
        </div>
        <span className="font-bold text-sm">ATLAS Dashboard</span>
      </Link>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                active
                  ? "bg-[var(--accent-blue)]/10 text-[var(--accent-blue)]"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5"
              }`}
            >
              <span
                className={`w-6 h-6 rounded-md flex items-center justify-center text-xs font-bold ${
                  active
                    ? "bg-[var(--accent-blue)]/20 text-[var(--accent-blue)]"
                    : "bg-white/5 text-[var(--text-muted)]"
                }`}
              >
                {item.icon}
              </span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Back to site */}
      <div className="px-3 pb-5">
        <Link
          href="/"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
        >
          <span>&larr;</span> Back to ForgeVoice
        </Link>
      </div>
    </aside>
  );
}

function MobileNav() {
  const pathname = usePathname();

  return (
    <div className="lg:hidden sticky top-0 z-50 bg-[var(--bg-secondary)] border-b border-white/5">
      <div className="flex items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-gradient-to-br from-[var(--accent-blue)] to-[var(--accent-purple)] flex items-center justify-center">
            <span className="text-white text-xs font-black">A</span>
          </div>
          <span className="font-bold text-sm">ATLAS</span>
        </Link>
      </div>
      <nav className="flex overflow-x-auto px-2 pb-2 gap-1 scrollbar-hide">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                active
                  ? "bg-[var(--accent-blue)]/10 text-[var(--accent-blue)]"
                  : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 min-w-0">
        <MobileNav />
        <main className="p-4 md:p-6 lg:p-8 max-w-7xl">{children}</main>
      </div>
    </div>
  );
}
