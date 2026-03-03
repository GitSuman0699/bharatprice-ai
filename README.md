# 🏷️ BharatPrice AI

> AI-powered hyperlocal pricing intelligence for Kirana stores

**Built for the [AI for Bharat Hackathon](https://vision.hack2skill.com/event/ai-for-bharat), organized by Hack2skill and powered by AWS.**

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
│       (Hosted on AWS Amplify CI/CD, Static Export)   │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (X-API-Key Secured)
┌──────────────────────▼──────────────────────────────┐
│               AWS API Gateway (HTTP API)             │
│                        │                            │
│           AWS Lambda (FastAPI Backend)               │
│  Intent Classification → Cache Check → Response Gen  │
└──────┬─────────┬───────────┬──────────────┬─────────┘
       │         │           │              │
┌──────▼───────┐ │  ┌────────▼───────┐ ┌───▼───────────────┐
│ Amazon       │ │  │ AWS DynamoDB   │ │  Live Data APIs   │
│ Bedrock      │ │  │ (Cache + TTL)  │ │  data.gov.in      │
│ (Claude 3    │ │  │                │ │  (AGMARKNET)      │
│  Haiku)      │ │  └────────────────┘ └───────────────────┘
│ AI Reasoning │ │
└──────────────┘ │
          ┌──────▼──────────┐
          │  BigBasket       │
          │  Scraper (httpx) │
          │  Live retail     │
          │  price scraping  │
          └─────────────────┘
```

## 🛠️ Tech Stack & Justifications

### Frontend — **Next.js 16 (Static Export) + TypeScript + Vanilla CSS**

| Choice | Why this? | Why not alternatives? |
|--------|-----------|-----------------------|
| **Next.js 16** | Static export (`output: 'export'`) generates pure HTML/CSS/JS — perfect for hosting on AWS Amplify with zero server costs. Built-in routing, image optimization, and SEO support out of the box. | **React CRA** — no built-in SSG/routing. **Vite** — great for SPAs but lacks the file-based routing and export features. **Plain HTML** — not scalable for multi-page apps with shared layouts. |
| **TypeScript** | Catches type errors at compile time, provides IDE autocompletion for API response shapes, and makes refactoring safer — critical when the API shape changes. | **JavaScript** — no compile-time safety, harder to maintain as the codebase grows. |
| **Vanilla CSS** | Full control over design, no build-time overhead, no framework lock-in. Our UI is simple enough (chat interface) that a CSS framework adds more complexity than it saves. | **Tailwind** — adds build complexity and utility class bloat for a single-page chat UI. **MUI/Chakra** — too heavy for a chat-only interface, increases bundle size. |

### Backend — **Python 3.11 + FastAPI + Mangum**

| Choice | Why this? | Why not alternatives? |
|--------|-----------|-----------------------|
| **Python 3.11** | First-class AWS SDK support (`boto3`), rich ecosystem for NLP/data processing, and the language of choice for the `data.gov.in` API client and web scraping (`httpx`, `BeautifulSoup`). | **Node.js** — weaker data processing libraries, less natural for scraping. **Go** — faster but smaller ML/AI ecosystem and longer dev time. |
| **FastAPI** | Async-native, automatic OpenAPI docs (`/docs`), Pydantic validation for request/response schemas, and exceptional performance for a Python framework. | **Flask** — no async, no built-in validation, manual OpenAPI. **Django** — too heavy for a stateless API (we don't need ORM, admin, templates). **Express.js** — would require rewriting all Python data-processing logic. |
| **Mangum** | A drop-in ASGI adapter that wraps our FastAPI app for AWS Lambda — zero code changes needed between local dev and production. | **Zappa/Serverless** — more complex setup, heavier abstractions. **Custom handler** — reinventing the wheel for ASGI-to-Lambda bridging. |
| **Pydantic** | Type-safe request/response validation with automatic error messages. Integrates natively with FastAPI — one model serves as validation + serialization + documentation. | **Marshmallow** — more verbose, doesn't auto-generate docs. **Manual validation** — error-prone and repetitive. |

### AI — **Amazon Bedrock (Claude 3 Haiku)**

| Choice | Why this? | Why not alternatives? |
|--------|-----------|-----------------------|
| **Claude 3 Haiku** | Fastest and cheapest model in the Claude family (~$0.25/M input tokens). Excellent at following structured prompts, formatting with markdown/emojis, and reasoning over JSON data contexts — perfect for a pricing assistant. | **Claude 3 Sonnet/Opus** — 4-20× more expensive, overkill for price formatting. **GPT-4o-mini** — comparable but requires OpenAI billing (this is an AWS hackathon). **Llama 3** — self-hosting adds infra complexity. |
| **Amazon Bedrock** | Fully managed, pay-per-token, no GPU instances to manage. Native AWS IAM integration means no API keys to rotate — Lambda's execution role handles auth automatically. | **SageMaker** — requires managing endpoints, instance types, auto-scaling. **Direct API** — requires managing API keys, billing outside AWS. **Self-hosted** — GPU instances are expensive and complex for a hackathon. |

### Infrastructure — **AWS Lambda + API Gateway + Amplify + DynamoDB**

| Choice | Why this? | Why not alternatives? |
|--------|-----------|-----------------------|
| **AWS Lambda** | Pay-per-request pricing (free tier: 1M requests/month), zero idle costs, auto-scales instantly, and integrates natively with Bedrock and DynamoDB via IAM roles. | **EC2/ECS** — always-on costs even with zero traffic. **Fargate** — minimum running costs. For a hackathon demo with sporadic traffic, serverless is the clear winner. |
| **API Gateway (HTTP API)** | Cheapest API Gateway option ($1/M requests), built-in CORS, automatic Lambda integration, and supports custom domains. | **REST API** — 3.5× more expensive, features we don't need (request validation, caching). **ALB** — requires always-on targets. |
| **AWS Amplify** | Git-push deployment — push to `master` and Amplify auto-builds the Next.js static export. Free SSL, CDN distribution, custom domains, and preview deployments. | **S3 + CloudFront** — manual setup for CI/CD, SSL, and invalidations. **Vercel** — excellent but outside AWS ecosystem (hackathon requirement). **Netlify** — same issue. |
| **DynamoDB** | Serverless NoSQL with built-in TTL (auto-deletes expired cache entries). Pay-per-request pricing, millisecond latency, and zero maintenance. Perfect for our cache-aside pattern. | **ElastiCache/Redis** — always-on costs, requires VPC config. **S3** — too slow for cache lookups. **RDS** — overkill for key-value caching, requires provisioned instances. |

### Data Sources — **data.gov.in (AGMARKNET) + BigBasket Scraper**

| Choice | Why this? | Why not alternatives? |
|--------|-----------|-----------------------|
| **data.gov.in AGMARKNET** | Official Government of India API with real mandi wholesale prices across 2,000+ mandis. Free, reliable, and updated daily. Provides the "ground truth" wholesale price. | **No alternative** — this is the only free, official source for Indian mandi prices. |
| **BigBasket Scraper (httpx)** | Provides real retail competitor prices via BigBasket's internal API. Scraped data is normalized to per-kg pricing and cached in DynamoDB with 24h TTL. | **Official BigBasket API** — doesn't exist publicly. **Selenium/Playwright** — too heavy for Lambda (headless browser). **httpx** is lightweight and async-compatible. |
| **Seed Data Fallback** | When live APIs fail (network issues, rate limiting), the app falls back to estimated prices based on historical patterns — ensuring the user always gets a response. | **No fallback** — unacceptable UX. Users should never see "no data available" for common products. |

## 📁 Project Structure

```text
bharatprice-ai/
├── amplify.yml                  # AWS Amplify CI/CD build spec
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point & CORS
│   │   ├── config.py            # Environment configuration (Pydantic Settings)
│   │   ├── middleware/          # Security & Rate Limiting (slowapi)
│   │   ├── models/              # Pydantic data models (ChatRequest, PriceData)
│   │   ├── routes/              # Chat & Health API endpoints
│   │   ├── services/
│   │   │   ├── ai_engine.py     # Bedrock AI integration & prompt engineering
│   │   │   ├── database.py      # DynamoDB cache-aside pattern
│   │   │   ├── price_fetcher.py # Orchestrates mandi API + scraper data
│   │   │   └── scraper.py       # BigBasket live price scraper (httpx)
│   │   └── data/                # Seed data & product mappings (fallback)
│   ├── deploy_backend.ps1       # Lambda automated deployment script
│   └── requirements.txt
├── frontend/
│   ├── next.config.ts           # Next.js static export & image config
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── chat/page.tsx    # Interactive chat UI (with chat history)
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
