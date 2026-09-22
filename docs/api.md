# AutoService AI - REST API Reference

## Authentication
- `POST /api/v1/auth/register` - Create owner account & default business
- `POST /api/v1/auth/login` - Obtain JWT access token
- `GET /api/v1/auth/me` - Fetch current authenticated profile

## Customer Enquiries
- `POST /api/v1/enquiries` - Intake natural language message, extract requirements, detect missing info, update lead score.

## CRM & Lead Management
- `GET /api/v1/leads?business_id=...` - List leads sorted by activity
- `PATCH /api/v1/leads/{lead_id}/status` - Update pipeline stage (NEW -> QUALIFIED -> QUOTED -> FOLLOW_UP -> BOOKED -> LOST)

## Quotations
- `POST /api/v1/quotations/calculate` - Pure deterministic pricing breakdown
- `POST /api/v1/quotations` - Create quotation in PENDING_APPROVAL status
- `GET /api/v1/quotations/{quote_id}/pdf` - Download PDF quotation
- `POST /api/v1/quotations/{quote_id}/approve` - Human owner approval trigger

## Reporting & Revenue Analytics
- `GET /api/v1/reports/daily?business_id=...` - Generate daily business report & net contribution

## Admin & Emergency Control
- `POST /api/v1/admin/emergency-stop` - Instantly activate emergency killswitch
- `POST /api/v1/admin/emergency-stop/deactivate` - Resume normal operations
- `GET /api/v1/admin/emergency-stop/status` - Check current safety state
