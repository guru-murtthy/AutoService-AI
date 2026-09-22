# AutoService AI - Operational Pilot Runbook

## Overview
This runbook guides daily operations, system monitoring, and emergency procedures during Phase 12 pilot execution.

---

## 1. Daily Health Checklist
1. **API & Health Metrics**:
   - Check `GET /health` (`status == "healthy"`).
   - Check `GET /ready` (`database == "connected"`).
2. **Worker Status**:
   - Inspect `worker.log` or check `worker_health` in `/health`.
3. **Pending Quotations**:
   - Log in to dashboard at `http://localhost:3000` to review quotes in `PENDING_APPROVAL` status.

---

## 2. Operational Procedures

### Activating Emergency Stop
If suspicious behavior or an operational error occurs:
- Call `POST /api/v1/admin/emergency-stop` or click **ACTIVATE EMERGENCY STOP** on the dashboard `/emergency` page.
- This immediately halts all background automation, outbound messaging, and agent tool execution.

### Resuming Operations
- Call `POST /api/v1/admin/emergency-stop/deactivate` or click **Resume Normal Operations** on `/emergency`.

---

## 3. Log Inspection
- Backend Server Logs: `backend.log`
- Background Worker Logs: `worker.log`
- System Audit Trail: `GET /api/v1/admin/audit-logs`
