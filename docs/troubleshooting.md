# AutoService AI - Troubleshooting Guide

## Common Issues & Diagnostics

### 1. Backend Fails to Start (Database Connection Error)
- Check `DATABASE_URL` in `.env`.
- Default fallback uses `sqlite:///./autoservice.db`.
- Ensure write permissions in project directory.

### 2. AI Provider API Failure
- If `GEMINI_API_KEY` is missing or invalid, the provider automatically falls back to the deterministic Regex Natural Language Parser (`_rule_based_extraction`).
- Check logs for `"Falling back to Rule Parser"`.

### 3. Emergency Stop Active
- If API calls return `400 / 500` or agent tasks fail with `SafetyPolicyViolation`, check `/api/v1/admin/emergency-stop/status`.
- Resume operations via UI or `POST /api/v1/admin/emergency-stop/deactivate`.
