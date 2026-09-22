# AutoService AI - Phase 12 Implementation Plan: Real-World Pilot Deployment

## Goal Description
Transform **AutoService AI** from a local pilot-ready application into a **publicly deployable, customer-testable SaaS pilot** ready for onboarding its first real travel/car-rental business in India (target: ₹5,000/month recurring revenue).

Phase 12 implements production configuration validation, PostgreSQL persistence & connection health checks, strict multi-tenant isolation security, public customer chat validation & prompt injection defenses, customer opt-out handling ("do not contact me"), human approval workflows, audit logging, rate limiting (HTTP 429), security HTTP headers, pilot settings management APIs, pilot value analytics, and comprehensive automated test verification.

---

## User Review Required

> [!IMPORTANT]
> **Production CORS & Secret Validation**: In production (`ENVIRONMENT=production`), wildcard CORS (`*`) will be rejected. The app will strictly require explicit origins configured via `CORS_ORIGINS` and fail at startup if production secrets are missing.

> [!NOTE]
> **Safety Guardrails**: Payments, mass outreach, autonomous spending, and self-modification remain strictly disabled (`PAYMENTS_ENABLED=false`, `AUTONOMOUS_SPENDING_ENABLED=false`).

---

## Proposed Changes

### Component 1: Audit & Environment Configuration
- [NEW] `docs/phase-12-audit.md` (Already created)
- [NEW] `.env.production.example` (Template for production environment variables)
- [MODIFY] `backend/app/core/config.py` (Add production secret validation, `ENVIRONMENT`, `CORS_ORIGINS`, `PUBLIC_BASE_URL`, feature flags)

### Component 2: Production Database & Health Verification
- [NEW] `docs/database-production.md` (PostgreSQL setup, migrations, backups, connection pooling, rollback)
- [MODIFY] `backend/app/core/database.py` (Add connection pool settings, startup verification check, prevent silent table creation in production if migrations pending)

### Component 3: Business Tenant Onboarding & Profile Settings API
- [MODIFY] `backend/app/models/all_models.py` (Add Business profile fields: `location`, `gst_number`, `logo_url`, `contact_person`, pilot metadata: `pilot_business`, `pilot_started_at`, `pilot_ends_at`, `pilot_status`)
- [NEW] `backend/app/api/routes/settings.py` (Endpoints for `/settings/business`, `/settings/pricing`, `/settings/notifications`, `/settings/integrations`, `/settings/security`)

### Component 4: Tenant Isolation Security Enforcer & Audit
- [MODIFY] `backend/app/api/routes/` (`leads.py`, `quotations.py`, `dashboard.py`, `reports.py`, `pricing.py`, `settings.py`) to mandate `verify_business_access` on all routes
- [NEW] `tests/test_tenant_security_audit.py` (Automated multi-tenant isolation tests for all major resources returning HTTP 403)

### Component 5: Customer Public Chat, Input Validation & Prompt Injection Defenses
- [MODIFY] `backend/app/schemas/all_schemas.py` (Pydantic validation for phone, name, duration > 0, passenger_count > 0, valid travel dates)
- [MODIFY] `backend/app/ai/provider.py` (Harden prompt templates against prompt injection attacks, sanitize outputs)
- [NEW] `tests/test_prompt_injection.py` (Automated prompt injection security test suite)
- [NEW] `tests/test_customer_validation.py` (Input validation tests)

### Component 6: Quotation System & Human Approval Workflow
- [MODIFY] `backend/app/models/all_models.py` & `backend/app/api/routes/quotations.py` (Add quote states: `VIEWED`, `EXPIRED`, `CANCELLED`, `BOOKED`, `LOST`)
- [MODIFY] Human approval checks for high-value quotes, large discounts, manual price overrides, refunds

### Component 7: Follow-Up Engine & Customer Opt-Out Mechanism
- [MODIFY] `backend/app/services/followup_service.py` (Detect opt-out phrases "stop", "unsubscribe", "opt out", "do not contact"; mark status as `OPTED_OUT`, cancel scheduled follow-ups)
- [NEW] `tests/test_opt_out.py` (Customer opt-out automated tests)

### Component 8: Customer CRM Board & Pilot Dashboard
- [MODIFY] `backend/app/models/all_models.py` (Lead status: `NEW`, `QUALIFYING`, `QUOTED`, `FOLLOW_UP`, `BOOKED`, `LOST`, `CANCELLED`, `OPTED_OUT`)
- [MODIFY] `backend/app/api/routes/dashboard.py` & `frontend/src/pages/Dashboard.tsx` (Display real pilot analytics, estimated time saved, "No data yet" indicators when data is empty)

### Component 9: Audit Logging & Production Error Handling
- [NEW] `backend/app/audit/logger.py` (Audit log helper tracking login, pricing change, quote approval, price override, settings change, emergency stop)
- [MODIFY] `backend/app/main.py` (Global Exception Handler returning clean JSON errors without leaking stack traces or internal paths)

### Component 10: Rate Limiting & Security Headers
- [NEW] `backend/app/core/rate_limiter.py` (Rate limiting middleware returning `429 Too Many Requests` on `/chat/*`, `/auth/*`, quote & AI routes)
- [NEW] `backend/app/core/security_headers.py` (Security HTTP headers middleware: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Strict-Transport-Security`)

### Component 11: Production Documentation & Runbooks
- [NEW] `docs/deployment.md` (Vercel, Render/Railway, Supabase/Neon PostgreSQL)
- [NEW] `docs/customer-onboarding.md` (Checklist for onboarding first real business)
- [NEW] `docs/pilot-runbook.md` (Operational procedures, pilot monitoring)
- [NEW] `docs/incident-response.md` (Outage handling, bad pricing recovery, rollback)
- [NEW] `docs/phase-12-performance.md` (Concurrency load benchmarks)

### Component 12: Comprehensive Test Suite & Final Verification
- Run full pytest suite (target: 100% pass rate across all unit, tenant security, prompt injection, idempotency, opt-out, and E2E pilot tests).
