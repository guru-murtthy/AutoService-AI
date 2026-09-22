#!/usr/bin/env bash
set -e

echo "=== AutoService AI Setup Script ==="

# Check Python version
if command -v python3 &>/dev/null; then
    echo "[✓] Python3 found: $(python3 --version)"
else
    echo "[✗] Python3 is required but not installed."
    exit 1
fi

# Check Node version
if command -v node &>/dev/null; then
    echo "[✓] Node found: $(node -v)"
else
    echo "[✗] Node.js is required but not installed."
    exit 1
fi

# Check Docker
if command -v docker &>/dev/null; then
    echo "[✓] Docker found: $(docker -v)"
else
    echo "[!] Docker not found. Local python/node fallback will be used."
fi

# Create backend virtualenv if not existing
if [ ! -d "backend/venv" ]; then
    echo "[+] Creating Python virtual environment in backend/venv..."
    python3 -m venv backend/venv
fi

source backend/venv/bin/activate
echo "[+] Installing backend dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r backend/requirements.txt

# Create .env from .env.example if missing
if [ ! -f ".env" ]; then
    echo "[+] Creating .env from .env.example..."
    cp .env.example .env
fi

echo "[+] Initializing Database tables..."
python3 -c "from app.core.database import init_db; init_db()"

echo "[+] Running backend test suite..."
pytest backend/tests/ -v --tb=short

echo "=== Setup Completed Successfully! ==="
echo "To start backend server: source backend/venv/bin/activate && uvicorn app.main:app --reload --port 8000"
