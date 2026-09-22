# AutoService AI 🚀

**"Autonomous AI operations for travel and local service businesses."**

AutoService AI is a B2B AI monorepo built for travel agencies and car-rental/tour operators in India, targeting **₹5,000/month recurring revenue** per business.

---

## 🌟 Key Features

1. **Customer Enquiry Intake & Natural Language Extraction**: Extracts origin, destination, vehicle, travel date, duration, passenger count, and budget.
2. **Missing-Information Detection**: Asks ONLY for missing fields without repeating answered questions.
3. **Deterministic Pricing Engine**: Strict code-level pricing math for Indian travel operators (base rates, per-km charges, driver allowances, GST 5%). **LLM is never permitted to set prices.**
4. **Professional PDF Quotation Generator**: ReportLab-powered PDF generation.
5. **Human Approval Workflow**: High-value quotes require explicit business owner approval before sending.
6. **Automated Follow-Up Engine**: Scheduled 24h, 48h, 72h check-ins with automatic response suppression.
7. **CRM Lead Board**: Pipeline management with engagement score badges.
8. **Daily Business Reports**: Summary of enquiries, quotes, bookings, revenue, AI costs, and net contribution.
9. **Emergency Killswitch**: `POST /api/v1/admin/emergency-stop` instantly halts outbound actions and agent execution.
10. **Conway Automaton Adapter**: Seamless integration with external Automaton runtime, with fallback to internal worker loop.

---

## 🏗 Monorepo Structure

```
autonomous-service/
├── frontend/               # React + TypeScript + Vite + Tailwind CSS Dashboard
├── backend/                # FastAPI Python Server & REST API
├── agent/                  # Autonomous Agent Core (OBSERVE-THINK-PLAN-ACT) & Safety Engine
├── automaton-adapter/      # Conway Automaton Integration Adapter & Fallback Bridge
├── worker/                 # Background Heartbeat Worker Loop
├── database/               # Database Models & Schemas
├── docker/                 # Containerization & docker-compose setup
├── docs/                   # Full Architecture, API, Agent, Security & Setup Docs
├── tests/                  # Unit, Safety, Integration & E2E Test Suite
└── scripts/                # Automated Setup Scripts (setup.sh)
```

---

## 🛠 Quickstart Setup

### Automated Installation
```bash
./scripts/setup.sh
```

### Manual Commands

#### 1. Backend Server
```bash
source backend/venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 2. Background Worker
```bash
source backend/venv/bin/activate
python3 -m app.workers.main
```

#### 3. Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```

Visit the SaaS Dashboard at: `http://localhost:3000`

---

## 🧪 Running Tests

```bash
source backend/venv/bin/activate
pytest tests/ -v
```

---

## 📚 Documentation Links
- [Architecture Overview](docs/architecture.md)
- [Setup & Quickstart](docs/setup.md)
- [REST API Reference](docs/api.md)
- [Autonomous Agent & Tools](docs/agent.md)
- [Security & Killswitch](docs/security.md)
- [Business & Pricing Strategy](docs/business-model.md)
- [Deployment Guide](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)
