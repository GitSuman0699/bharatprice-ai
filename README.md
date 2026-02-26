# 🏷️ BharatPrice AI

> AI-powered hyperlocal pricing intelligence for India's 12M+ kirana stores

[![AI for Bharat Hackathon](https://img.shields.io/badge/AI%20for%20Bharat-Hackathon%202026-FF6B2C)](https://hack2skill.com)
[![Powered by AWS](https://img.shields.io/badge/Powered%20by-AWS%20Bedrock-232F3E)](https://aws.amazon.com/bedrock/)

## 🎯 Problem Statement

Small kirana store owners across India lack access to real-time competitive pricing data. They set prices based on gut feeling, leading to lost margins or customers. With 12M+ kirana stores serving 80%+ of India's retail, this is a massive, underserved market.

## 💡 Solution

BharatPrice AI is a conversational AI assistant that helps kirana store owners:

- **Get smart price recommendations** — AI-generated optimal selling prices based on mandi rates, competitor data, and local averages
- **Compare competitor prices** — See how your prices stack up against BigBasket, JioMart, and local market averages
- **Track mandi wholesale rates** — Find the cheapest mandi to buy from across Azadpur, Vashi, Koyambedu, and 20+ mandis
- **Analyze price trends** — Understand if prices are rising, falling, or stable over 30-day windows
- **Forecast demand** — Get alerts about upcoming festivals, seasons, and weather events that impact demand

All in **Hindi, English, Tamil, Telugu, and Marathi** — with voice input support.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Custom Web Chat UI                   │
│               (Next.js / TypeScript)                 │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend (Python)                 │
│  Intent Classification → AI Engine → Response Gen    │
└──────┬───────────────────────────────────┬──────────┘
       │                                   │
┌──────▼──────────┐              ┌────────▼──────────┐
│  Amazon Bedrock  │              │  Seed Data Layer   │
│  (Claude 3)      │              │  50+ products      │
│  AI Reasoning    │              │  8 cities           │
└─────────────────┘              │  30-day history     │
                                 └────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) AWS credentials for Bedrock integration

### Backend

```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000` with API docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

## 📊 Features Demo

| Feature | How to Try |
|---------|-----------|
| Price Check | "Aaj atta ka rate kya hai?" |
| Hindi Support | "टमाटर का भाव बताओ" |
| Competitor Compare | "Compare onion prices in Mumbai" |
| Mandi Rates | "Mandi rates for potato" |
| Price Trends | "Price trend of rice" |
| Product Catalog | "Show all products" |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Vanilla CSS |
| Backend | Python, FastAPI, Pydantic |
| AI | Amazon Bedrock (Claude 3 Haiku) |
| Data | Seed data engine (DynamoDB-ready) |
| Languages | Hindi, English, Tamil, Telugu, Marathi |
| Voice | Web Speech API (browser-based) |

## 📁 Project Structure

```
bharatprice-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── models/schemas.py    # Pydantic data models
│   │   ├── routes/
│   │   │   ├── chat.py          # Chat endpoint
│   │   │   ├── data.py          # Price/mandi/trend endpoints
│   │   │   └── user.py          # User profile endpoints
│   │   ├── services/
│   │   │   ├── ai_engine.py     # AI + intent classification
│   │   │   └── database.py      # Data access layer
│   │   └── data/
│   │       └── seed_data.py     # Realistic seed data generator
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── chat/page.tsx    # Interactive chat UI
│   │   │   ├── layout.tsx       # Root layout
│   │   │   └── globals.css      # Design system
│   │   └── lib/api.ts           # API client
│   └── package.json
├── design.md                    # System design document
├── requirements.md              # Requirements & user stories
└── README.md
```

## 👥 Team

**BharatPrice AI** — AI for Bharat Hackathon 2026

## 📄 License

MIT
