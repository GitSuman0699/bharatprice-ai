# Requirements: BharatPrice AI

## Overview
BharatPrice AI is an AI-powered hyperlocal pricing intelligence platform for India's kirana store owners. It delivers smart pricing recommendations and demand forecasts via a WhatsApp chatbot in Hindi/regional languages.

---

## User Stories

### US-001: Price Recommendation Query
**As a** kirana store owner,
**I want to** ask for today's recommended selling price of a product via WhatsApp,
**So that** I can price competitively and maximize my margins.

**Acceptance Criteria:**
- User can send a text or voice message asking about any product's price
- System responds within 5 seconds with a recommended price
- Response includes: suggested price, local average, competitor range, and margin estimate
- Response is in the user's preferred language (Hindi/English/regional)

---

### US-002: Voice Input in Vernacular
**As a** shopkeeper with limited tech literacy,
**I want to** send a voice message in Hindi or my regional language,
**So that** I can use the tool without typing.

**Acceptance Criteria:**
- System accepts WhatsApp voice notes as input
- Speech is transcribed and translated to extract product and intent
- Response is sent back as both text and voice note in the same language

---

### US-003: Competitor Price Comparison
**As a** store owner,
**I want to** compare my prices with nearby stores and online platforms,
**So that** I know if I'm overpricing or underpricing.

**Acceptance Criteria:**
- System shows the user's price vs nearby competitors, BigBasket, JioMart, and local average
- Visual indicators (⬆️⬇️✅) show if user is above, below, or at market price
- Data is refreshed daily

---

### US-004: Demand Forecast Alerts
**As a** shopkeeper,
**I want to** receive proactive alerts about upcoming demand spikes,
**So that** I can stock up in advance and set optimal prices.

**Acceptance Criteria:**
- System sends automated alerts 3–7 days before festivals, weather events, or seasonal trends
- Alert includes: affected products, expected demand increase %, and recommended stock action
- Alerts are sent via WhatsApp push notification

---

### US-005: Mandi Rate Tracking
**As a** kirana store owner who buys wholesale,
**I want to** check real-time mandi prices for products across nearby mandis,
**So that** I can buy at the lowest wholesale rate.

**Acceptance Criteria:**
- User can query mandi rates by product name
- System returns prices from 3–5 nearest mandis with location names
- Data is sourced from Agmarknet and updated daily

---

### US-006: User Onboarding & Profile
**As a** new user,
**I want to** set up my store profile (location, product categories, store size),
**So that** the system gives me personalized recommendations.

**Acceptance Criteria:**
- Onboarding flow collects: store name, location (pin code), product categories, and preferred language
- Entire onboarding completes within a 5-message WhatsApp conversation
- Profile can be updated anytime via a simple command

---

### US-007: Price History & Trends
**As a** shopkeeper,
**I want to** view how a product's price has changed over the past weeks/months,
**So that** I can understand pricing trends and plan ahead.

**Acceptance Criteria:**
- User can query price history for any tracked product
- System responds with a text-based trend summary (e.g., "Atta price rose 12% in last 30 days")
- Trend direction (rising/falling/stable) is clearly indicated

---

## Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-01 | System shall accept text and voice inputs via WhatsApp Business API | High |
| FR-02 | System shall transcribe voice input using Amazon Transcribe | High |
| FR-03 | System shall support Hindi, English, Tamil, Telugu, and Marathi | High |
| FR-04 | System shall aggregate pricing data from Agmarknet, ONDC, and e-commerce APIs daily | High |
| FR-05 | System shall generate AI-powered price recommendations using Amazon Bedrock | High |
| FR-06 | System shall predict demand using seasonal, festival, and weather data | Medium |
| FR-07 | System shall send proactive stock-up alerts via WhatsApp | Medium |
| FR-08 | System shall maintain user profiles with store location and preferences | High |
| FR-09 | System shall provide competitor price benchmarking | Medium |
| FR-10 | System shall respond to queries within 5 seconds | High |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| NFR-01 | System shall handle 10,000+ concurrent users | Medium |
| NFR-02 | System shall have 99.9% uptime | High |
| NFR-03 | System shall comply with data privacy regulations | High |
| NFR-04 | System shall work on low-bandwidth connections (< 2G) | Medium |
| NFR-05 | All AI responses shall include a confidence disclaimer | High |
