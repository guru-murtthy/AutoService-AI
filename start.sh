#!/usr/bin/env bash
set -e

echo "======================================================"
echo "      Starting AutoService AI Monorepo Services       "
echo "======================================================"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# 1. Ensure Python Virtual Environment exists
if [ ! -d "backend/venv" ]; then
    echo "[+] Creating Python virtual environment..."
    python3 -m venv backend/venv
    source backend/venv/bin/activate
    pip install --quiet --upgrade pip
    pip install --quiet -r backend/requirements.txt
fi

source backend/venv/bin/activate
export PYTHONPATH="$ROOT_DIR/backend:$ROOT_DIR"

# 2. Ensure Database Tables are initialized
python3 -c "from app.core.database import init_db; init_db()"

echo "[+] Starting Backend FastAPI Server on http://localhost:8000..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "    Backend running (PID: $BACKEND_PID, logs: backend.log)"

echo "[+] Starting Background Heartbeat Worker..."
nohup python3 -m app.workers.main > worker.log 2>&1 &
WORKER_PID=$!
echo "    Worker running (PID: $WORKER_PID, logs: worker.log)"

echo "[+] Starting Frontend Vite SaaS Dashboard on http://localhost:3000..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "[+] Installing frontend dependencies..."
    npm install
fi

echo "======================================================"
echo "  All services launched successfully!                "
echo "  - Dashboard UI: http://localhost:3000              "
echo "  - REST API:     http://localhost:8000/api/v1       "
echo "  - Health Check: http://localhost:8000/health       "
echo "======================================================"

npm run dev -- --host 0.0.0.0 --port 3000
