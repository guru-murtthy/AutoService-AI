# AutoService AI - Setup Guide

## Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Docker & Docker Compose (optional for containerized setup)

## Quick Installation

Run the automated setup script:
```bash
./scripts/setup.sh
```

## Running Manually

### 1. Backend API
```bash
source backend/venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Background Heartbeat Worker
```bash
source backend/venv/bin/activate
python3 -m app.workers.main
```

### 3. Frontend SaaS Dashboard
```bash
cd frontend
npm install
npm run dev
```

Visit dashboard at `http://localhost:3000`.
