import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LMS×DR — Learning Management × Demand Radar",
  description:
    "AI-powered platform combining business opportunity analysis with structured learning paths. 12 opportunities scored across 8 dimensions with implementation roadmaps.",
  viewport: "width=device-width, initial-scale=1, maximum-scale=5",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
