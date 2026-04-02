# 🏷️ BharatPrice AI

> AI-powered hyperlocal pricing intelligence for Kirana stores

**Built for the [AI for Bharat Hackathon](https://vision.hack2skill.com/event/ai-for-bharat) and optimized for seamless free-tier deployment.**

[![AI for Bharat Hackathon](https://img.shields.io/badge/AI%20for%20Bharat-Hackathon%202026-FF6B2C)](https://vision.hack2skill.com/event/ai-for-bharat)

## 🎯 Problem Statement
Kirana store owners lack access to real-time competitive pricing data. They set prices based on gut feeling, leading to lost margins.

## 💡 Solution
BharatPrice AI is a conversational web-based AI assistant that helps kirana store owners:
- **Get smart price recommendations** — AI-generated optimal selling prices based on live mandi rates.
- **Compare competitor prices** — Compare your prices with online platforms like BigBasket, JioMart, etc. (if data is available for that region).
- **Track mandi wholesale rates** — Find the current wholesale rates for commodities across India.

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────┐
│                 Next.js Web Chat UI                  │
│             (Hosted globally on Vercel)              │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (CORS Secured)
┌──────────────────────▼──────────────────────────────┐
│           FastAPI Backend (Hosted on Render)         │
│  Intent Classification → Cache Check → Response Gen  │
└──────┬─────────┬───────────┬──────────────┬─────────┘
       │         │           │              │
┌──────▼───────┐ │  ┌────────▼───────┐ ┌───▼───────────────┐
│ Groq API     │ │  │ SQLite Db      │ │  Live Data APIs   │
│ (Llama 3.3)  │ │  │ (Local Data &  │ │  data.gov.in      │
│ Fast LLM     │ │  │ TTL Caching)   │ │  (AGMARKNET)      │
│ Reasoning    │ │  └────────────────┘ └───────────────────┘
└──────────────┘ │
          ┌──────▼──────────┐
          │  BigBasket       │
          │  Scraper (httpx) │
          │  Live retail     │
          │  price scraping  │
          └─────────────────┘
```

## 🛠️ Tech Stack & Justifications

### Frontend — **Next.js 16 + TypeScript + Vanilla CSS**

| Choice | Why this? |
|--------|-----------|
| **Next.js 16** | Generates highly optimized frontend UI. Deploys seamlessly on Vercel. Built-in routing, image optimization, and SEO support out of the box. |
| **TypeScript** | Catches type errors at compile time, provides IDE autocompletion for API response shapes, and makes refactoring safer. |
| **Vanilla CSS** | Full control over design, no build-time overhead, no framework lock-in. Our UI is simple enough that a CSS framework adds more complexity than it saves. |

### Backend — **Python 3.12 + FastAPI + SQLite**

| Choice | Why this? |
|--------|-----------|
| **Python 3.12** | Rich ecosystem for NLP/data processing, and the language of choice for the `data.gov.in` API client and web scraping (`httpx`, `BeautifulSoup`). |
| **FastAPI** | Async-native, automatic OpenAPI docs (`/docs`), Pydantic validation for request schemas, and exceptional performance. |
| **SQLite** | Zero-configuration local database. Perfect for fast cache-aside data retrieval and easy deployment on free-tier services. |
| **Pydantic** | Type-safe request/response validation with automatic error messages. |

### AI — **Groq (Llama 3.3)**

| Choice | Why this? |
|--------|-----------|
| **Groq (Llama 3.3)** | Llama 3 on Groq's LPU inference engine provides near-instantaneous responses. Extremely fast generation speed provides the best user experience for a conversational pricing bot. |

### Infrastructure — **Vercel + Render**

| Choice | Why this? |
|--------|-----------|
| **Vercel** | Git-push deployment for the Next.js frontend. Free SSL, CDN distribution, and custom domains. Perfect serverless hosting. |
| **Render** | Simple free-tier hosting for the FastAPI Python backend. Auto-deploys cleanly from GitHub branches. |

### Data Sources — **data.gov.in (AGMARKNET) + BigBasket Scraper**

| Choice | Why this? |
|--------|-----------|
| **data.gov.in AGMARKNET** | Official Government of India API with real mandi wholesale prices across 2,000+ mandis. Free, reliable, and updated daily. |
| **BigBasket Scraper (httpx)** | Provides real retail competitor prices via BigBasket's internal API. Scraped data is normalized to per-kg pricing. |
| **Seed Data Fallback** | When live APIs fail (network issues, rate limiting), the app falls back to estimated prices based on historical patterns. |

## 📁 Project Structure

```text
bharatprice-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point & CORS
│   │   ├── config.py            # Environment configuration
│   │   ├── middleware/          # Security & Rate Limiting
│   │   ├── models/              # Pydantic data models
│   │   ├── routes/              # Chat & Health API endpoints
│   │   ├── services/
│   │   │   ├── ai_engine.py     # Groq API integration (Llama 3)
│   │   │   ├── database.py      # SQLite implementation & cache-aside pattern
│   │   │   ├── price_fetcher.py # Orchestrates mandi API + scraper data
│   │   │   └── scraper.py       # BigBasket live price scraper (httpx)
│   │   └── data/                # Seed data & product mappings (fallback)
│   ├── .python-version          # Python version configuration for Render
│   └── requirements.txt
├── frontend/
│   ├── next.config.ts           # Next.js export & image config
│   ├── .env.production          # Vercel Production connection vars
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── chat/page.tsx    # Interactive chat UI
│   │   │   ├── layout.tsx       # Root layout
│   │   │   └── globals.css      # Design system
│   │   └── lib/api.ts           # API client wrapper
│   └── package.json
└── README.md
```

## 📄 License
MIT
