# Design: BharatPrice AI

## System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                  │
│               Next.js Web Chat Application              │
│               (Deployed on AWS Amplify)                 │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS / REST
┌──────────────────────▼──────────────────────────────────┐
│                    API GATEWAY LAYER                    │
│             AWS API Gateway (HTTP API)                  │
│             (CORS & Preflight Handling)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   COMPUTE LAYER                         │
│             AWS Lambda (FastAPI Python)                 │
│       (API Key Validation, Rate Limiting)               │
└──────────┬───────────────────┬────────────────┬─────────┘
           │                   │                │
┌──────────▼───────────┐ ┌─────▼──────────┐ ┌───▼─────────────┐
│     AI PROCESSING    │ │HOT CACHE LAYER │ │  DATA SOURCES   │
│    Amazon Bedrock    │ │Amazon DynamoDB │ │  data.gov.in    │
│  (Claude 3 Haiku)    │ │(via TTL index) │ │  (AGMARKNET)    │
└──────────────────────┘ └────────────────┘ └─────────────────┘
```

## Component Design

### 1. Web Frontend (Next.js)
- **Technology:** Next.js 16 (Static Export), React, TypeScript, Vanilla CSS.
- **Function:** Provides a fully-styled, glassmorphism chat interface for users to ask pricing questions.
- **Deployment:** AWS Amplify CI/CD connected directly to the GitHub repository (Monorepo setup).

### 2. Backend API (FastAPI)
- **Technology:** Python 3.11, FastAPI, Pydantic, Mangum (for Lambda adaptation).
- **Function:** Receives chat messages, fetches live context data, and queries the LLM.
- **Deployment:** AWS Lambda deployed via standard zip packaging. AWS API Gateway HTTP API handles routing and CORS preflight explicitly. Managed via PowerShell automation.

### 3. AI Reasoning Engine (Amazon Bedrock)
- **Model:** Anthropic Claude 3 Haiku (`anthropic.claude-3-haiku-20240307-v1:0`).
- **Function:** Evaluates user intent, processes raw agricultural data returned by the data fetcher, and generates natural language price recommendations. Capable of processing English, Hindi, and regional language text natively.
- **Competitor Comparison:** The AI is prompted to compare proposed prices against known online marketplace rates (like BigBasket, JioMart, etc.) if data is provided in the prompt context or available within the model's localized knowledge base.

### 4. Live Data Integration
- **Source:** Government of India Open Data API (`data.gov.in`).
- **Function:** Provides real-time and historical wholesale Mandi rates for various commodities across Indian states and districts.

### 5. Hot Caching Layer (DynamoDB)
- **Technology:** Amazon DynamoDB.
- **Function:** The `data.gov.in` API limits requests and can be slow. We store the daily mandi rates for requested states in DynamoDB to return them instantly on subsequent queries.
- **Eviction Strategy:** DynamoDB Time-to-Live (TTL) is heavily utilized. Cache records are set to automatically expire after 24 hours, ensuring the AI always provides completely fresh mandi rates the next day without manual cache purging.

## Security Architecture

- **API Authentication:** Custom `APIKeyMiddleware` validates an `X-API-Key` header for all protected routes (e.g., `/api/chat`).
- **CORS Handling:** Managed natively by AWS API Gateway (`OPTIONS` method) to allow secure cross-origin requests from the Amplify frontend, avoiding preflight rejection.
- **Rate Limiting:** IP-based requests are throttled using `slowapi` to prevent API endpoint abuse and AWS billing runaways.
- **API Hiding:** `/docs` and `/redoc` Swagger documentation endpoints are programmatically hidden when executing inside the production AWS Lambda environment.
- **IAM:** Lambda execution role is strictly scoped, currently utilizing managed policies for `AmazonBedrockFullAccess` and standard execution.
