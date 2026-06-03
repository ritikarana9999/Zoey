# SmartCart AI - Grocery Price Intelligence Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat&logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=flat&logo=typescript)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-powered grocery price tracking, forecasting, and basket optimization across Australian supermarkets.**

SmartCart AI tracks prices across Woolworths, Coles, and Aldi — giving shoppers real-time intelligence on where to buy, when to buy, and how much to save. Machine learning forecasts predict price changes before they happen.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SmartCart AI                             │
├────────────────┬──────────────────┬───────────────┬────────────┤
│   Next.js 14   │   FastAPI        │  PostgreSQL   │   Redis    │
│   Frontend     │   Backend        │   Database    │   Cache    │
│                │                  │               │            │
│  - Dashboard   │  - REST API      │  - Products   │  - Session │
│  - Products    │  - ML Services   │  - Prices     │  - Queue   │
│  - Basket      │  - Forecasting   │  - Forecasts  │  - Cache   │
│  - Forecasts   │  - AI Assistant  │  - Analytics  │            │
│  - Chat AI     │  - Price Tracker │               │            │
└────────────────┴──────────────────┴───────────────┴────────────┘
        │                  │
        └──── Docker Compose ────┘

ML Stack:
┌──────────────┬──────────────┬──────────────┬──────────────────┐
│   XGBoost    │  Scikit-learn│  Statsmodels │  OpenAI GPT-4    │
│  Price Fcst  │  Similarity  │  ARIMA/SARIMA│  AI Assistant    │
└──────────────┴──────────────┴──────────────┴──────────────────┘
```

---

## Features

### Price Intelligence
- **Real-time price tracking** across Woolworths, Coles, and Aldi
- **180-day price history** with interactive charts
- **Price alerts** when items drop to 90-day lows
- **Sale detection** with discount % and savings amount
- **Unit price normalization** (per 100g/100ml comparison)

### AI Forecasting
- **XGBoost price forecasting** — 30-day price predictions per product/store
- **Inflation analytics** — category and basket-level inflation detection
- **Seasonal pattern detection** — identifies recurring price cycles
- **Price volatility index** — coefficient of variation per product

### Smart Basket
- **Multi-store basket optimization** — split basket across stores for maximum savings
- **Basket builder** — add products, see total cost per store
- **Store comparison** — side-by-side basket cost across all stores
- **Saved baskets** — persist shopping lists with optimization results

### Recommendations
- **Product alternatives** — cheaper substitutes with similar nutritional profile
- **"Buy now or wait" signal** — based on 90-day price history
- **Category savings map** — which categories have biggest price ranges

### AI Assistant
- **Natural language queries** — "When is milk cheapest at Woolworths?"
- **GPT-4 powered** with SmartCart context injection
- **Actionable responses** with product links and price data

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI, Python 3.11, SQLAlchemy 2.0 |
| Database | PostgreSQL 15, Redis 7 |
| ML/AI | XGBoost, Scikit-learn, Statsmodels, OpenAI |
| Infra | Docker Compose, GitHub Actions |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) OpenAI API key for AI assistant

### 1. Clone and configure

```bash
git clone https://github.com/your-org/smartcart-ai.git
cd smartcart-ai

# Copy environment template
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY if desired
```

### 2. Start services

```bash
docker-compose up -d
```

### 3. Seed the database with sample data

```bash
docker-compose --profile seed run data_seeder
```

### 4. Access the app

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## API Documentation

### Core Endpoints

#### Products
```
GET  /api/products               List products with filters
GET  /api/products/{id}          Get product details
GET  /api/products/{id}/prices   Price history across stores
GET  /api/products/search?q=     Full-text search
```

#### Prices
```
GET  /api/prices/current         Latest prices all products
GET  /api/prices/history/{id}    Price history for product
GET  /api/prices/top-movers      Biggest price changes today
GET  /api/prices/alerts          Products near 90-day low
```

#### Forecasts
```
GET  /api/forecasts/{product_id}           30-day price forecast
GET  /api/forecasts/category/{category_id} Category price outlook
POST /api/forecasts/generate               Trigger model retraining
```

#### Basket
```
POST /api/basket                 Create/save basket
GET  /api/basket/{id}            Get saved basket
POST /api/basket/optimize        Optimize basket across stores
POST /api/basket/compare         Compare basket total per store
```

#### Analytics
```
GET  /api/analytics/inflation          Category inflation rates
GET  /api/analytics/store-comparison   Store price index
GET  /api/analytics/summary            Dashboard summary stats
GET  /api/analytics/top-movers         Price movement leaderboard
```

#### AI Assistant
```
POST /api/assistant/chat         Send message, get AI response
GET  /api/assistant/suggestions  Context-aware query suggestions
```

---

## Development

### Backend (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://smartcart:smartcart_secret@localhost:5432/smartcart
export REDIS_URL=redis://localhost:6379

uvicorn main:app --reload
```

### Frontend (without Docker)

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend type checking
cd frontend
npm run type-check
```

---

## Database Schema

```
categories ──┐
             ├── products ──┬── store_products ── price_history
stores ──────┘             │
                           ├── forecasts
                           ├── recommendations
                           └── product_embeddings

users ── baskets
```

---

## Deployment

### Production with Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | (required) |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | JWT signing secret | (required) |
| `OPENAI_API_KEY` | OpenAI key for AI assistant | (optional) |
| `NEXT_PUBLIC_API_URL` | Backend API URL for frontend | `http://localhost:8000` |

---

## Screenshots

### Dashboard
> Real-time price intelligence with inflation tracking across all categories.

### Price Charts
> Interactive 180-day price history with moving averages and sale markers.

### Basket Optimizer
> Build your shopping list and see which store combination saves the most.

### AI Assistant
> Ask questions in plain English about prices, trends, and savings opportunities.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

Built with love for Australian grocery shoppers.
