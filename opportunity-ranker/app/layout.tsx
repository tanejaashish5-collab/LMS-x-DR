import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hidden Gold Mines — AI Business Opportunity Ranker",
  description:
    "Interactive 3D comparison of the top AI-powered business opportunities for 2026. Data-driven rankings across 8 dimensions.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen grid-bg">{children}</body>
    </html>
  );
}
