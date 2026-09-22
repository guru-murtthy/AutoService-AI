# AutoService AI - Production & Pilot Setup Guide

## 1. Environment Configuration (`.env`)

Create `.env` in the root directory:

```ini
APP_ENV=production
APP_MODE=pilot            # 'pilot' mode enforces safety while using real DB & AI
DEMO_MODE=false           # Set true for isolated demo businesses
LOG_LEVEL=INFO

PORT=8000
HOST=0.0.0.0

# Security (CRITICAL: Generate a strong random key in production)
JWT_SECRET=generate-a-strong-secret-key-32-chars-minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Configuration (PostgreSQL for production/pilot, SQLite for local dev)
DATABASE_URL=postgresql://user:password@localhost:5432/autoservice_prod

# AI Provider Settings (Gemini Primary)
AI_PROVIDER=gemini
GEMINI_API_KEY=your_real_gemini_api_key_here
AI_TIMEOUT_SECONDS=12
AI_MAX_RETRIES=3

# Conway Automaton Integration
AUTOMATON_URL=http://localhost:9000
AUTOMATON_API_KEY=your_automaton_secret_key

# Financial Safety Limits (₹ INR)
DAILY_SPENDING_LIMIT=500.0
MONTHLY_SPENDING_LIMIT=5000.0
APPROVAL_THRESHOLD=10000.0
```

---

## 2. Database Migrations (PostgreSQL)

Run Alembic migrations to initialize PostgreSQL schema:
```bash
source backend/venv/bin/activate
cd backend
alembic upgrade head
```

---

## 3. Starting Pilot Services

### Backend REST API
```bash
source backend/venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Background Heartbeat Worker
```bash
source backend/venv/bin/activate
python3 -m app.workers.main
```

### Frontend SaaS Dashboard & Public Web Chat
```bash
cd frontend
npm install
npm run build
npm run preview -- --port 3000
```
