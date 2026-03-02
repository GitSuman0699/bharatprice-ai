# Requirements: BharatPrice AI (Current Implementation)

## Overview
BharatPrice AI is an AI-powered hyperlocal pricing intelligence platform for India's kirana store owners. It delivers smart pricing recommendations via a web-based chat interface connected to live government data.

---

## User Stories

### US-001: Price Recommendation Query
**As a** kirana store owner,
**I want to** ask for today's recommended selling price of a product via the web chat,
**So that** I can price competitively and maximize my margins.

**Acceptance Criteria:**
- User can send a text message asking about a product's price (e.g., "what are the tomato prices in New Delhi").
- System responds with a recommended price based on actual real-time data.
- Response includes: suggested retail price, mandi wholesale rate, and profit margin estimate.

### US-002: Real-time Mandi Rate Tracking
**As a** kirana store owner who buys wholesale,
**I want to** check real-time mandi prices for products,
**So that** I can buy at the lowest wholesale rate.

**Acceptance Criteria:**
- System queries the live `data.gov.in` AGMARKNET API in the background.
- System extracts relevant state/market data and uses it as context for the AI response.

### US-003: Multilingual Text Support
**As a** shopkeeper,
**I want to** ask questions in Hindi or English,
**So that** I can use the tool in my preferred language.

**Acceptance Criteria:**
- AI model (Claude 3 Haiku) natively understands and responds to Hindi, English, and other regional text input within the web chat interface.

---

### US-004: Competitor Price Comparison
**As a** store owner,
**I want to** compare my prices with online platforms like BigBasket and JioMart,
**So that** I know if I'm overpricing or underpricing my local customers.

**Acceptance Criteria:**
- System analyzes user's query and fetches or infers current online platform prices (if available).
- Response includes a comparison point against these popular online platforms to help the user benchmark their retail price.

---

## Functional Requirements

| ID | Requirement | Status |
|----|------------|----------|
| FR-01 | System shall accept text inputs via the Next.js web chat interface | ✅ Implemented |
| FR-02 | System shall aggregate live pricing data from data.gov.in (AGMARKNET) | ✅ Implemented |
| FR-03 | System shall cache live pricing data points for 24 hours in DynamoDB via TTL to prevent rate-limiting | ✅ Implemented |
| FR-04 | System shall generate AI-powered price recommendations using Amazon Bedrock | ✅ Implemented |
| FR-05 | System shall provide a secure API layer via API Key authentication | ✅ Implemented |
| FR-06 | System shall protect against abuse using IP-based rate limiting | ✅ Implemented |

## Non-Functional Requirements

| ID | Requirement | Status |
|----|------------|----------|
| NFR-01 | System shall be deployed as a serverless application (AWS Lambda/Amplify) for zero-maintenance scaling | ✅ Implemented |
| NFR-02 | API endpoints shall be secured via HTTPS, CORS preflight handling, and Trusted Hosts middleware | ✅ Implemented |
| NFR-03 | All AI responses shall include a confidence disclaimer regarding market fluctuations | ✅ Implemented |
