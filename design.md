# Design: BharatPrice AI

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                  │
│         WhatsApp Business API  /  Voice (IVR)           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│               INGESTION & NLP LAYER (AWS)               │
│  API Gateway → Transcribe → Translate → Intent Router   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  AI PROCESSING LAYER                    │
│  Amazon Bedrock (GenAI)  │  SageMaker (Forecasting)    │
└──────────┬───────────────────────────┬──────────────────┘
           │                           │
┌──────────▼───────────┐  ┌────────────▼─────────────────┐
│    STORAGE LAYER     │  │     DATA PIPELINE LAYER      │
│  DynamoDB │ S3 │     │  │  Lambda + EventBridge +      │
│  ElastiCache         │  │  Step Functions              │
└──────────────────────┘  └────────────┬─────────────────┘
                                       │
                          ┌────────────▼─────────────────┐
                          │     EXTERNAL DATA SOURCES    │
                          │  Agmarknet │ ONDC │ Govt     │
                          │  E-commerce │ IMD Weather    │
                          └──────────────────────────────┘
```

---

## Component Design

### 1. WhatsApp Interface Service
- **Technology:** WhatsApp Business API (Meta Cloud API)
- **Function:** Receives user messages (text/voice), routes to backend, delivers responses
- **Webhook:** Registered with API Gateway endpoint
- **Message Types:** Text, voice note, interactive buttons

### 2. NLP & Language Service
- **Amazon Transcribe:** Converts voice notes to text (supports Hindi, Tamil, Telugu, Marathi, English)
- **Amazon Translate:** Translates regional language input to English for processing
- **Amazon Comprehend:** Extracts entities (product name, location) and detects intent
- **Amazon Polly:** Converts text response back to voice note in user's language

### 3. AI Reasoning Engine
- **Amazon Bedrock (Claude/Titan):**
  - Understands user query intent (price check, comparison, forecast)
  - Generates personalized price recommendations with reasoning
  - Produces natural language responses in vernacular
- **Prompt Template:** Structured prompt with user profile, product data, market context, and competitor prices

### 4. Demand Forecasting Service
- **Amazon SageMaker:**
  - Time-series model trained on historical price + sales data
  - Inputs: weather forecasts, festival calendar, seasonal patterns
  - Output: Predicted demand change % per product per region

### 5. Data Pipeline
- **AWS EventBridge:** Triggers daily data collection at 6 AM IST
- **AWS Lambda:** Scraper functions for each data source
- **AWS Step Functions:** Orchestrates ETL — scrape → clean → transform → store
- **Data Sources:**
  - Agmarknet API → Mandi wholesale prices
  - ONDC API → Marketplace listing prices
  - Consumer Affairs Portal → Government retail price bulletins
  - IMD API → Weather forecasts
  - Custom dataset → Indian festival/event calendar

### 6. Storage

| Store | Technology | Purpose |
|-------|-----------|---------|
| User Profiles | DynamoDB | Store location, preferences, language |
| Price Data | DynamoDB | Daily prices by product, location, source |
| Raw Data | S3 | Raw scraped data for auditing |
| Real-time Cache | ElastiCache (Redis) | Frequently queried prices for fast response |

---

## Data Flow

### Query Flow (User asks for price)
```
User (WhatsApp) → API Gateway → Lambda
  → Transcribe (if voice) → Translate (if regional)
  → Comprehend (extract product + intent)
  → Bedrock (generate recommendation using DynamoDB data)
  → Translate (back to user's language)
  → Polly (if voice response needed)
  → WhatsApp API → User
```

### Data Ingestion Flow (Daily automated)
```
EventBridge (6 AM cron) → Step Functions
  → Lambda scrapers (Agmarknet, ONDC, Govt, Weather)
  → S3 (raw data)
  → Transform Lambda (clean + normalize)
  → DynamoDB (structured price data)
  → ElastiCache (hot cache update)
```

### Alert Flow (Proactive notifications)
```
EventBridge (daily check) → Lambda
  → SageMaker (demand prediction)
  → Bedrock (generate alert message)
  → Translate + Polly
  → WhatsApp API → Subscribed Users
```

---

## API Design

### Internal APIs (Lambda Functions)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/whatsapp` | POST | Receives WhatsApp messages |
| `/query/price` | POST | Processes price recommendation query |
| `/query/compare` | POST | Fetches competitor comparison |
| `/query/mandi` | POST | Returns nearby mandi rates |
| `/query/trend` | POST | Returns price history/trends |
| `/user/profile` | POST/PUT | Creates or updates user profile |
| `/alerts/forecast` | GET | Triggers demand forecast alerts |
| `/data/ingest` | POST | Triggers manual data ingestion |

---

## Database Schema

### Users Table (DynamoDB)
```json
{
  "userId": "wa_919876543210",
  "storeName": "Ramesh General Store",
  "pinCode": "110001",
  "city": "Delhi",
  "language": "hi",
  "categories": ["grocery", "dairy", "snacks"],
  "createdAt": "2026-02-14T10:00:00Z"
}
```

### Prices Table (DynamoDB)
```json
{
  "productId": "atta_10kg",
  "date": "2026-02-14",
  "region": "delhi_central",
  "mandiPrice": 280,
  "oncdPrice": 310,
  "bigbasketPrice": 335,
  "jioMartPrice": 320,
  "localAvg": 325,
  "recommendedRetail": 320,
  "demandTrend": "rising",
  "source": "agmarknet,ondc,scraper"
}
```

---

## Security & Privacy
- All data encrypted at rest (S3, DynamoDB) and in transit (TLS 1.2+)
- No personal customer data stored — only store owner profiles
- WhatsApp messages are not stored beyond processing
- IAM roles with least-privilege access for all Lambda functions
- API Gateway with rate limiting and WAF protection

---

## Scalability
- **Serverless architecture** — Lambda auto-scales with demand
- **DynamoDB on-demand** — scales read/write capacity automatically
- **ElastiCache** — reduces Bedrock calls for repeated queries
- **Regional deployment** — ap-south-1 (Mumbai) for low latency
