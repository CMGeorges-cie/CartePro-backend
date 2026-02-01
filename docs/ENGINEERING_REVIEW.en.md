# Engineering Review (EN)

## Summary
The backend is functional and organized around Flask blueprints. The core flows (auth, cards CRUD, admin listing) are present, but there are several correctness, reliability, and testing gaps that should be addressed.

## Issues & Risks
1. **User serialization inconsistency**
   - Two `serialize()` methods existed; the last one overrode the first and dropped `stripe_customer_id`.
   - Fixed in code by consolidating a single serializer that includes Stripe metadata.

2. **Public card view mismatch**
   - `GET /view/<int:card_id>` uses an integer converter while `Card.id` is a UUID string.
   - Template `view_card.html` is referenced but not present.
   - Impact: route will 404 for valid UUIDs and template rendering fails.

3. **Input validation gaps**
   - Card creation allows missing `name`, `title`, or `email` even though the model requires them.
   - Expect DB integrity errors in production, returning 500s instead of 4xx.

4. **Backup location ambiguity**
   - Admin backup listing uses `os.getcwd()` which can vary by process manager.
   - Consider using `app.instance_path` or a configured path.

5. **Stripe config calls are brittle**
   - `/api/v1/stripe/config` calls Stripe without guarding against missing keys or network failure.
   - Consider feature flagging or returning a safe payload when not configured.

6. **Rate limiting storage**
   - Rate limit storage is in-memory. In production, this does not scale and resets on restart.

## Missing Tests
- **Public routes**: `GET /health`, `GET /view/<card_id>`.
- **QR**: `POST /api/v1/qr/generate` success and validation error paths.
- **Stripe**: `/config` with mocked Stripe SDK and `/webhook` event handling.
- **Admin**: export CSV/JSON responses, restore endpoints, and non-admin access control.
- **Cards**: create validation errors, deleted card access, pro limit enforcement.
- **Auth**: avatar upload validation and file handling.

## Recommendations
1. Add validation for required fields in card creation and updates.
2. Align public card view route to UUID, add missing template or remove route.
3. Centralize backup directory in configuration.
4. Add defensive handling for Stripe config when keys are missing.
5. Expand test coverage for public/QR/Stripe/admin error paths.
