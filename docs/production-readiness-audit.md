# AutoService AI - Production Readiness Audit

**Audit Date**: September 22, 2026  
**Auditor**: Software Architecture & Security Lead  
**Scope**: Full Monorepo (`backend/`, `frontend/`, `agent/`, `automaton-adapter/`, `worker/`)

---

## Executive Summary

The MVP codebase for AutoService AI successfully demonstrates deterministic pricing, AI requirement extraction, quotation generation, and safety killswitch mechanics. However, moving to **Phase 11 (Real-World Validation / Pilot Mode)** requires resolving critical multi-tenant authorization gaps, adding customer-facing web chat interfaces, enforcing idempotency, creating business pricing profiles, and expanding AI resiliency.

---

## Detailed Audit Findings

### 1. Tenant Isolation & Authorization Enforcement
- **Classification**: **CRITICAL**
- **Location**: `backend/app/api/routes/leads.py`, `quotations.py`, `dashboard.py`, `reports.py`
- **Finding**: API endpoints accept `business_id` as a query parameter or payload field without verifying that `current_user` belongs to or owns that `business_id`.
- **Impact**: Cross-tenant data leak. A user authenticated under Business A could access or mutate Business B's customers, leads, quotations, and financial reports.
- **Remediation**: Create a `verify_business_access(business_id, current_user, db)` security dependency enforcing tenant scoping on every route.

### 2. Missing Public Customer Web Chat Interface
- **Classification**: **HIGH**
- **Location**: `frontend/src/pages/`, `backend/app/api/routes/`
- **Finding**: The MVP features an admin sandbox visualizer, but lacks a dedicated customer-facing web chat portal at `/chat/{business_id}`.
- **Impact**: Real customers cannot directly submit enquiries, supply missing trip details, or receive generated PDF quotations online.
- **Remediation**: Build public `/chat/{business_id}` web chat UI backed by persistent FastAPI WebSocket/REST messaging endpoints.

### 3. Missing Idempotency Controls
- **Classification**: **HIGH**
- **Location**: `backend/app/services/enquiry_service.py`, `quotations.py`, `followup_service.py`
- **Finding**: Operations such as enquiry processing, quotation creation, and booking creation lack idempotency token verification (`Idempotency-Key` or transaction reference uniqueness).
- **Impact**: Duplicate webhooks or double-clicks create duplicate leads, duplicate quotations, and double bookings.
- **Remediation**: Implement an idempotency middleware/utility storing processed idempotency keys with a 24-hour expiration.

### 4. AI Provider Failure & Rate-Limit Resiliency
- **Classification**: **HIGH**
- **Location**: `backend/app/ai/provider.py`
- **Finding**: While a rule-based regex fallback exists, the AI client lacks exponential backoff, retries on HTTP 429 (rate limit) or 5xx errors, structured JSON validation, and sanitized performance logging (provider, model, latency, cost estimate without exposing API keys).
- **Impact**: Intermittent AI API rate limits cause immediate fallback rather than retrying gracefully.
- **Remediation**: Add an HTTP retry mechanism with exponential backoff and sanitized telemetry logging.

### 5. Messaging Abstraction Layer
- **Classification**: **MEDIUM**
- **Location**: `backend/app/notifications/`
- **Finding**: Channel dispatching is ad-hoc rather than routed through a unified `MessagingProvider` interface with `WebChatProvider` and official `WhatsAppBusinessProvider` (Cloud API) implementations.
- **Impact**: Hard to plug in official WhatsApp Business API or alternative channels cleanly.
- **Remediation**: Implement `MessagingProvider` abstract base class with `WebChatProvider` and `WhatsAppBusinessProvider` implementations.

### 6. Business-Specific Pricing Profiles & Terms
- **Classification**: **MEDIUM**
- **Location**: `backend/app/pricing/engine.py`, `backend/app/models/all_models.py`
- **Finding**: Pricing currently falls back to global `DEFAULT_RATES` if `PricingConfig` is not set. Businesses also cannot configure included km/day, cancellation policies, terms & conditions, or quote validity days via API/UI.
- **Impact**: One-size-fits-all pricing does not fit different Indian travel operators' policies.
- **Remediation**: Expand `PricingConfig` and `Business` models to support full pricing profiles and management endpoints.

### 7. Pilot Mode (`APP_MODE=pilot`) & Demo Mode (`DEMO_MODE=true`) Configuration
- **Classification**: **HIGH**
- **Location**: `backend/app/core/config.py`
- **Finding**: System supports `development` and `production`, but lacks `pilot` mode (real DB, real AI, real web chat, real quotes, disabled payments/mass outreach) and `DEMO_MODE=true` (visually isolated demo data).
- **Impact**: Risk of executing real payment or outreach logic during initial pilot validation.
- **Remediation**: Add `APP_MODE=pilot` and `DEMO_MODE=true` handling across safety policy and frontend UI indicators.

### 8. Observability & Health Check Metrics Expansion
- **Classification**: **LOW**
- **Location**: `backend/app/main.py`, `frontend/src/pages/Dashboard.tsx`
- **Finding**: `/health`, `/ready`, and `/metrics` return basic static information and do not report Conway Automaton health, background worker status, database dialect, task failure rates, or AI latency.
- **Impact**: Reduced operational visibility during pilots.
- **Remediation**: Expand observability endpoints and display status indicators on dashboard header.

---

## Verification Matrix

| Component | Current State | Phase 11 Required State | Status |
| :--- | :--- | :--- | :--- |
| **Database** | SQLite local file | Dual SQLite / PostgreSQL via `DATABASE_URL` + Migrations | Pending |
| **Tenant Scoping** | Unchecked query params | Server-enforced `verify_business_access` | Pending |
| **Customer Chat** | Admin sandbox visualizer | Public `/chat/{business_id}` web chat UI | Pending |
| **Pricing Engine** | Code math + fallback rates | Business-specific rate profiles & policies | Pending |
| **Messaging** | Mock functions | `MessagingProvider` (WebChat + WhatsApp API stub) | Pending |
| **Idempotency** | None | Idempotency key tracking & de-duplication | Pending |
| **Pilot Mode** | None | `APP_MODE=pilot` & `DEMO_MODE=true` | Pending |
| **Observability** | Basic `/health` | Expanded `/health`, `/ready`, `/metrics` telemetry | Pending |
