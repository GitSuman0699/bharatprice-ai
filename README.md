# 🏷️ BharatPrice AI

> AI-powered hyperlocal pricing intelligence for Kirana stores

[![Powered by AWS](https://img.shields.io/badge/Powered%20by-AWS%20Bedrock-232F3E)](https://aws.amazon.com/bedrock/)

## 🎯 Problem Statement
Kirana store owners lack access to real-time competitive pricing data. They set prices based on gut feeling, leading to lost margins.

## 💡 Solution
BharatPrice AI is a conversational web-based AI assistant that helps kirana store owners:
- **Get smart price recommendations** — AI-generated optimal selling prices based on live mandi rates.
- **Track mandi wholesale rates** — Find the current wholesale rates for commodities across India.

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────┐
│                 Next.js Web Chat UI                  │
│       (Hosted on AWS Amplify CI/CD, Static Export)   │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (X-API-Key Secured)
┌──────────────────────▼──────────────────────────────┐
│               AWS API Gateway (HTTP API)             │
│                        │                            │
│           AWS Lambda (FastAPI Backend)               │
│  Intent Classification → Cache Check → Response Gen  │
└──────┬────────────────────┬──────────────┬───────────┘
       │                    │              │
┌──────▼──────────┐ ┌───────▼────────┐ ┌───▼───────────────┐
│  Amazon Bedrock │ │ AWS DynamoDB   │ │  Live Data APIs   │
│ (Claude 3 Haiku)│ │ (Caching + TTL)│ │  data.gov.in      │
│  AI Reasoning   │ │                │ │  (AGMARKNET)      │
└─────────────────┘ └────────────────┘ └───────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS credentials (for Bedrock and live deployment)
- Data.gov.in API Key

### Backend setup

```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory copying `.env.example`, then populate it with your AWS and Data.gov.in credentials.

Run locally:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Backend runs at `http://localhost:8000` with API docs at `http://localhost:8000/docs`

### Frontend setup

```bash
cd frontend
npm install
```

Create a `.env.local` file in the `frontend` directory:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=your_api_key_here
```

Run locally:
```bash
npm run dev
```
Frontend runs at `http://localhost:3000`

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16 (Static Export), TypeScript, Vanilla CSS |
| Backend | Python 3.11, FastAPI, Pydantic, Mangum |
| Deployment | AWS Amplify (Frontend), AWS Lambda + API Gateway (Backend) |
| Caching | Amazon DynamoDB (with TTL for 24-hour automatic eviction) |
| AI | Amazon Bedrock (Anthropic Claude 3 Haiku) |
| Data Source | data.gov.in (AGMARKNET Prices) |

## 📁 Project Structure

```text
bharatprice-ai/
├── amplify.yml                  # AWS Amplify CI/CD build spec
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point & CORS
│   │   ├── config.py            # Environment configuration
│   │   ├── middleware/          # Security & Rate Limiting (slowapi)
│   │   ├── models/              # Pydantic data models
│   │   ├── routes/              # Chat & Health API endpoints
│   │   ├── services/
│   │   │   ├── ai_engine.py     # Bedrock AI integration
│   │   │   └── data_fetcher.py  # Data.gov.in API integration
│   │   └── data/                # Fallback static datasets
│   ├── deploy_backend.ps1       # Lambda automated deployment script
│   └── requirements.txt
├── frontend/
│   ├── next.config.ts           # Next.js export & image config
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── chat/page.tsx    # Interactive chat UI
│   │   │   ├── layout.tsx       # Root layout
│   │   │   └── globals.css      # Design system
│   │   └── lib/api.ts           # Axios API client wrapper
│   └── package.json
├── design.md                    # System design document
├── requirements.md              # Requirements & user stories
└── README.md
```

## 📄 License
MIT
