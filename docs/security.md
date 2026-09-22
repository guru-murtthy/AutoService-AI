# AutoService AI - Security & Financial Safety

## Financial Safety Controls
- `DAILY_SPENDING_LIMIT`: Default ₹500/day
- `MONTHLY_SPENDING_LIMIT`: Default ₹5,000/month
- `APPROVAL_THRESHOLD`: Default ₹10,000 (Quotes above ₹10,000 require owner approval)

## Emergency Stop Killswitch
- `POST /api/v1/admin/emergency-stop` halts outbound messages, payments, and agent task execution immediately.
- The agent loop cannot override or disable the emergency stop.

## Authentication & Audit Logging
- JWT tokens signed with HS256 algorithm.
- Passwords hashed with bcrypt.
- Every state change recorded in `audit_logs` table with actor, action, resource_id, and metadata.
