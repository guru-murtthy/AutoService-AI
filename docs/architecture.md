# AutoService AI - System Architecture

## Overview
**AutoService AI** is an autonomous B2B AI business service monorepo built for travel agencies and car-rental operators in India.

## Monorepo Layout
- `frontend/`: React + TypeScript + Vite + Tailwind CSS SaaS Dashboard
- `backend/`: Python + FastAPI + SQLAlchemy DB models & REST APIs
- `agent/`: Autonomous Agent Core loop (`OBSERVE -> THINK -> PLAN -> ACT -> VERIFY -> RECORD -> LEARN`) & Safety Policy Engine
- `automaton-adapter/`: Conway Automaton bridge adapter & offline fallback handler
- `worker/`: Background heartbeat loop (5-min health, 15-min tasks, 1-hour follow-ups, 24-hour reporting)
- `docker/` & `docker-compose.yml`: Local multi-container orchestration
- `docs/`: Architectural, API, and Operational documentation
- `tests/`: Unit, safety, integration, and E2E test suite

## Core Design Principles
1. **Deterministic Logic vs AI Reasoning**:
   - AI handles natural language extraction, sentiment, scoring suggestions, summaries, and reply drafting.
   - Deterministic Python code handles pricing, rates, driver allowances, taxes (GST 5%), totals, DB writes, auth, spend caps, and audit logs.
2. **Business Validation Mode (`BUSINESS_VALIDATION_MODE=true`)**: Outbound messages and spending require human approval.
3. **Emergency Stop System**: `POST /api/v1/admin/emergency-stop` instantly halts outbound actions and autonomous agent tools.
