import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BharatPrice AI — Smart Pricing for Kirana Stores",
  description:
    "AI-powered hyperlocal pricing intelligence for India's 12M+ kirana store owners. Get real-time price recommendations, competitor comparisons, and demand forecasts in Hindi and English.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <nav className="navbar">
          <a href="/" className="navbar-brand">
            <span className="logo-icon">🏷️</span>
            <h1>BharatPrice AI</h1>
          </a>
          <div className="navbar-links">
            <a href="/#features">Features</a>
            <a href="/chat" className="btn-primary">
              Try Demo →
            </a>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
