# AutoService AI - Customer Onboarding Checklist

Use this checklist when onboarding the first real travel/car-rental business for pilot validation:

---

## Onboarding Checklist

- [ ] **1. Create Business & Owner Account**
  - Register owner account at `POST /api/v1/auth/register`.
  - Record `owner_id` and assigned `business_id`.

- [ ] **2. Configure Business Profile**
  - Navigate to `/settings` or call `POST /api/v1/settings/business/{business_id}`.
  - Set business name, phone, location, GST number, and contact person.

- [ ] **3. Configure Pricing Profiles**
  - Configure rates per vehicle category (`5-seater`, `7-seater`, `tempo-traveller`).
  - Set base price/day, included km/day (default 250km), extra km rate, driver allowance, cancellation policy, terms, and quote validity.

- [ ] **4. Test Public Customer Web Chat**
  - Open `https://app.domain.com/chat/{business_id}` on desktop and mobile browsers (360px, 390px, 768px).
  - Submit test enquiry: *"Need a 7 seater from Bangalore to Coorg for 3 days starting Oct 15 for 6 pax"*.
  - Verify AI requirement extraction, missing field check, and instant calculation output.

- [ ] **5. Test PDF Quotation Generation**
  - Download generated PDF quote link and verify line-item rates, driver allowance, and GST 5% calculations.

- [ ] **6. Verify Human Approval Workflow**
  - Verify quotes above approval threshold (`APPROVAL_THRESHOLD = ₹10,000`) appear in `PENDING_APPROVAL` status on owner dashboard.
  - Verify business owner can approve or modify quote before sending.

- [ ] **7. Test Customer Opt-Out Mechanism**
  - Submit opt-out message (*"Please stop contacting me"*).
  - Verify lead status changes to `OPTED_OUT` and automated follow-up check-ins stop permanently.

- [ ] **8. Activate Pilot Mode**
  - Confirm `APP_MODE=pilot` is active in `.env`.
