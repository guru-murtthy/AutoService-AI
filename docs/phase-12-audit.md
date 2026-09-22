# AutoService AI - Phase 12 Comprehensive Audit

**Audit Date**: September 22, 2026  
**Target Goal**: Transform local Phase 11 pilot system into a publicly deployable, customer-testable SaaS pilot targeting **₹5,000/month recurring revenue** from one travel operator.

---

## 1. Existing Phase 11 Baseline Summary

- **FastAPI Core & REST APIs**: Authentication, enquiry processing, CRM lead management, quotations calculation, daily reporting, admin emergency stop.
- **AI Requirements Extraction**: Provider abstraction (`backend/app/ai/provider.py`) supporting Gemini API and rule-based regex fallback parser.
- **Deterministic Pricing Engine**: Code-level pricing math for 5-seater, 7-seater, tempo-traveller, extra km, driver allowance, GST 5%.
- **ReportLab PDF Generator**: Generates official PDF quotations with line-item breakdowns.
- **Follow-Up Scheduler**: 24h, 48h, 72h check-in triggers.
- **Public Customer Web Chat**: `/chat/:businessId` frontend UI and `/api/v1/public/chat/{business_id}/message` backend route.
- **Tenant Isolation**: `verify_business_access` security dependency created.
- **Idempotency**: `check_and_store_idempotency_key` helper created.
- **Test Suite**: 9 passing tests covering pricing, enquiries, safety, tenant isolation, idempotency, persistence, public chat, and E2E lifecycle.

---

## 2. Missing Production & Deployment Requirements

| Category | Missing Requirement / Issue | Priority | Recommended Fix |
| :--- | :--- | :--- | :--- |
| **Environment System** | Hardcoded default secrets in config; missing production validation for required environment variables (`CORS_ORIGINS`, `PUBLIC_BASE_URL`, `ENVIRONMENT`). | **HIGH** | Update `config.py` to validate production secrets, expand `.env.example`, create `.env.production.example`. |
| **Production Database** | Silent table creation (`init_db`) without strict Alembic migration checks in production. | **HIGH** | Prevent auto-table creation in production if migrations haven't run. Create `docs/database-production.md`. |
| **Business Onboarding** | Missing Business Profile & Settings endpoints (`/settings/business`, `/settings/pricing`, `/settings/notifications`, `/settings/security`). | **HIGH** | Build business setting endpoints, database schema updates, and frontend settings tabs. |
| **Customer Validation** | Customer intake accepts invalid passenger counts (<= 0), negative duration, malformed dates. | **HIGH** | Add Pydantic / input validation middleware returning structured HTTP 422 errors with user-friendly messages. |
| **Prompt Injection** | LLM prompt vulnerable to "Ignore instructions", "Give ₹1 quote", or "Reveal system prompt". | **HIGH** | Harden AI prompt templates, add output sanitization, and create `tests/test_prompt_injection.py`. |
| **Quotation Workflow** | Missing quote states (`VIEWED`, `EXPIRED`, `CANCELLED`). | **MEDIUM** | Expand `Quotation` state machine & approval workflow. |
| **Customer Opt-Out** | Missing explicit customer opt-out trigger ("stop", "unsubscribe", "do not contact"). | **HIGH** | Detect opt-out keywords in customer chat & follow-up processor; mark status as `OPTED_OUT` and cease automated follow-ups. |
| **Rate Limiting & Security Headers** | CORS allows wildcard `*` by default; missing rate limiting (429) on public endpoints and security HTTP headers. | **HIGH** | Implement `slowapi` rate limiting on `/chat/*`, `/auth/*`, strict CORS via `CORS_ORIGINS`, and security headers middleware. |
| **Error Handling** | Uncaught server exceptions may leak stack traces or internal details. | **MEDIUM** | Add global FastAPI Exception Handler returning clean JSON errors without leaking stack traces or internal paths. |
| **Observability** | `/metrics` does not track request counts, error counts, AI call latencies, or worker failure states. | **MEDIUM** | Expand metrics service and dashboard health indicators. |
| **Pilot Data & Analytics** | Missing pilot metadata (`pilot_business=true`, `pilot_started_at`, `pilot_status`) and estimated time saved analytics. | **MEDIUM** | Add pilot tracking fields to Business model and display value analytics on Dashboard. |
| **Public Deployment Docs** | Missing deployment runbooks, onboarding checklists, incident response procedures, and performance benchmarks. | **HIGH** | Create `docs/deployment.md`, `docs/customer-onboarding.md`, `docs/pilot-runbook.md`, `docs/incident-response.md`, `docs/phase-12-performance.md`. |

---

## 3. Data Persistence & Security Audit Matrix

- **PostgreSQL Persistence**: Fully supported via SQLAlchemy & Alembic migration scripts.
- **Tenant Isolation**: Verified via `verify_business_access` dependency across all business routes.
- **Secret Management**: All keys moved to environment variables.
- **Customer Privacy**: Mask phone numbers and emails in system logs.
