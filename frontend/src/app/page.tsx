import Link from "next/link";

const features = [
  {
    icon: "🏷️",
    title: "Smart Price Recommendations",
    desc: "AI-generated optimal selling prices based on mandi rates, competitor prices, local averages, and demand trends.",
  },
  {
    icon: "📊",
    title: "Competitor Benchmarking",
    desc: "Compare your prices with BigBasket, JioMart, local markets, and nearby stores — know if you're over or under-pricing.",
  },
  {
    icon: "🏪",
    title: "Live Mandi Rates",
    desc: "Real-time wholesale prices from Azadpur, Vashi, Koyambedu, and 20+ major mandis across India.",
  },
  {
    icon: "📈",
    title: "Price Trend Analysis",
    desc: "Track how prices change over weeks and months. Spot rising trends early and plan your stock accordingly.",
  },
  {
    icon: "🔮",
    title: "Demand Forecasting",
    desc: "AI predicts demand spikes from festivals, weather, and seasonal patterns — stock up before prices rise.",
  },
  {
    icon: "🗣️",
    title: "Hindi & Regional Languages",
    desc: "Ask in Hindi, English, Tamil, Telugu, or Marathi. BharatPrice AI understands you in your language.",
  },
];

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-badge">
          🇮🇳 AI for Bharat Hackathon — Prototype
        </div>
        <h1>
          Smart Pricing for{" "}
          <span className="gradient-text">India&apos;s Kirana Stores</span>
        </h1>
        <p>
          AI-powered pricing intelligence that helps 12 million+ kirana store
          owners set optimal prices, track competitors, and forecast demand — all
          in Hindi and regional languages.
        </p>
        <div className="hero-cta">
          <Link href="/chat" className="btn-primary">
            🚀 Try the AI Demo
          </Link>
          <a href="#features" className="btn-secondary">
            Learn More ↓
          </a>
        </div>

        {/* Stats */}
        <div className="stats-bar">
          <div className="stat-item">
            <div className="stat-value">50+</div>
            <div className="stat-label">Products Tracked</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">8</div>
            <div className="stat-label">Major Cities</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">24+</div>
            <div className="stat-label">Mandis Covered</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">5</div>
            <div className="stat-label">Languages</div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section" id="features">
        <h2 className="section-title">
          Everything a Kirana Owner Needs
        </h2>
        <p className="section-subtitle">
          One AI assistant that replaces hours of market research
        </p>
        <div className="features-grid">
          {features.map((f, i) => (
            <div key={i} className="feature-card">
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section
        style={{
          textAlign: "center",
          padding: "80px 24px",
        }}
      >
        <h2 className="section-title">Ready to Price Smarter?</h2>
        <p
          className="section-subtitle"
          style={{ marginBottom: "32px" }}
        >
          Try BharatPrice AI now — ask about any product in Hindi or English
        </p>
        <Link href="/chat" className="btn-primary" style={{ fontSize: "16px", padding: "14px 32px" }}>
          🏷️ Start Chatting with BharatPrice AI
        </Link>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>
          Built with ❤️ for India — AI for Bharat Hackathon 2026 |{" "}
          Powered by AWS Bedrock & Indian Market Data
        </p>
      </footer>
    </>
  );
}
