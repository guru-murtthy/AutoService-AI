# AutoService AI - Incident Response Plan

## Incident Severity Matrix

| Severity | Definition | Action Required | Response SLA |
| :--- | :--- | :--- | :--- |
| **SEV-1 (Critical)** | Database outage, emergency stop failure, cross-tenant data leak | Trigger Emergency Stop, notify engineering lead immediately | < 15 mins |
| **SEV-2 (High)** | AI Provider outage (Gemini API 5xx/429), worker process crash | System automatically engages Rule Parser Fallback; restart worker | < 1 hour |
| **SEV-3 (Medium)** | Incorrect pricing config saved by owner, PDF rendering error | Update business pricing profile via `/settings`, regenerate PDF | < 4 hours |

---

## Response Procedures

### 1. AI Provider Outage (Gemini API 429/500)
- **Automatic Defense**: `backend/app/ai/provider.py` automatically catches errors, executes exponential backoff retries, and falls back to the deterministic Regex Rule Parser.
- **Manual Check**: Inspect `backend.log` for `"AI Provider unavailable/failed. Engaging Rule Parser Fallback."`

### 2. Bad Pricing Configuration / Incorrect Quote
- Navigating to `/settings` -> Pricing Profiles.
- Correct vehicle base rate or rate/km.
- Click **Save Changes** and recalculate quote.

### 3. Customer Complaint / Opt-Out Escalation
- If customer requests opt-out verbally or via chat, system automatically marks status as `OPTED_OUT`.
- Owner can manually update lead status to `OPTED_OUT` on the CRM board.
