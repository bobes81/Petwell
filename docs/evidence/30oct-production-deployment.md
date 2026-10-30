# Production deployment and evidence boundary — 30 October 2026

## Initial production deployment facts verified by the owner

- Existing Render service: `srv-d67jptusb7us73e9qbj0`.
- Deployed commit: **`f75dbe1c6fb9c16f3895a5b01451e2de4d9b9160`**.
- Build succeeded; all six project migrations succeeded: `accounts.0001`, `orders.0002`–`0005`, `products.0002_product_is_available`.
- The service is live/running in Render, but **Maintenance Mode remains enabled**. This is not a claim that the public storefront is open or that assessor/browser acceptance passed.
- These deployment facts were explicitly verified and supplied by the owner. The repository reviewer did not deploy, inspect the private dashboard or query production. No dashboard screenshot, exact deployment time, production data counts, backup boundary or cutover mechanism is invented here. This update does not assert that PR #8 was merged; deployment and merge are separate.

Later documentation commits on `fix/pp5-resubmission` are not automatically deployed. The production SHA above remains the release identity until a separately verified update. The earlier `6f0ac78` production baseline and pre-deployment NO-GO plans are historical references, not the current deployment state.

## Later owner-verified acceptance and current image issue

The owner subsequently verified on **30 October** that the public shop and cart function and **one real Stripe SANDBOX hosted checkout for GBP 11.49 succeeded**: the related production order is stored as paid, and its Checkout Session is complete and paid. This is a genuine owner-verified sandbox result, not a live-card charge or a mocked fixture. No order/Session identifier or customer details are published. The reviewer did not initiate another checkout or access the payment account. Exact destination-response evidence, duplicate-event handling, failure/retry and one-time cart reconciliation remain separate checks unless genuinely recorded.

The owner also confirms **Render auto-deploy is disabled**. The earlier maintenance-enabled statement records the initial deployment snapshot; it is not a new inspection of the current setting. Later public shop/cart success is owner verified. No maintenance/environment/deployment setting was changed by this review.

**Confirmed owner-reported defect:** all ten products have Cloudinary image references, but the live shop displays static fallback images. The actual original public `src` and Cloudinary HTTP response have not been verified, so missing/inaccessible assets are **not** established. [Image diagnosis and narrow code fix](../PRODUCT_IMAGE_DIAGNOSIS.md) distinguishes server-selected fallback, correctly generated URL and browser fallback after a delivery failure. The persisted reference shape already builds correctly from a configured database resource; a separately confirmed raw-string input bug is fixed on the PR branch, not claimed as the production root cause or as deployed.

## New owner observation: one original URL displays construction artwork

For Calming Lavender Spray, the original HTTPS Cloudinary URL was opened by the owner in Chrome and displayed PetWell construction/coming-soon artwork. The origin HTTP status was not captured; the reviewer proxy blocked its own request before the origin. [Exact public URL/source/scope](30oct-cloudinary-placeholder-observation.json). This establishes wrong displayed content for that observed mapping, not a missing asset. The other eight physical targets require their own review. [Prepared upload/guarded replacement procedure](../CATALOGUE_PLACEHOLDER_REPLACEMENT.md) requires separate owner approvals; no upload, asset overwrite/deletion or production write was performed.

## Automated application evidence

For the deployed application baseline: **SQLite 190 tests: 189 passed, one PostgreSQL-only skip; PostgreSQL 190 passed, no skips/failures**. [Saved SQLite output](29oct-release-handoff-sqlite.txt), [saved PostgreSQL 18.6 output](29oct-release-handoff-postgresql18.txt), [deployed commit's PR CI](https://github.com/bobes81/Petwell/actions/runs/41010383682), [push CI](https://github.com/bobes81/Petwell/actions/runs/41010379354). CI passed SQLite and PostgreSQL 16/18. These are application tests with mocked external adapters and genuine signed fixtures, not real provider acceptance. No local Django suite was rerun for this documentation update.

## Actual uploaded-backup rehearsal — independently executed locally

On 30 October the reviewer restored the owner's attached real backup into isolated disposable **PostgreSQL 18.6** and applied all six pending migrations once. A second unchanged restore of the same archive supplied the comparison baseline. [Sanitised machine result](30oct-real-backup-migration-rehearsal.json).

All original rows and original field values in **22 tables** were preserved. Original commerce/content counts remained **10 products, 5 orders, 5 order items, 2 posts and 2 subscribers**; these are restored-backup counts, not a new measurement of production. All five legacy orders have unique UUIDs and remain pending without invented Stripe proof; order-item links are intact. The legacy PDF record remains, and availability defaults true for all existing products: migration does not withdraw an offer. The only expected metadata additions were six migration rows, two model content types and eight permissions; original migration records remained unchanged. No migrations remained, and the local Django system check passed.

Disposable databases/container/network and private temporary files were removed; the original uploaded archive was retained unchanged. Only this aggregate result is published, with no dump, personal rows, credentials or customer/payment identifiers. The real-data migration gate, including `products.0002`, is complete; do not repeat the rehearsal by default.

## Still unverified — do not mark these passed

| Area | Genuine evidence still needed |
| --- | --- |
| Stripe sandbox | One GBP 11.49 hosted sandbox Checkout/complete paid Session/paid production order is owner verified above. Exact destination HTTP 200/correlation, replay, one-time cart clearing and decline/cancel/retry observations are not inferred from it. No additional payment is authorised here. |
| SMTP/password reset | Actual receipt in a controlled mailbox and successful secure reset link; environment compatibility, local in-memory email and console logs are not delivery. |
| Cloudinary/catalogue | Owner confirms ten existing references and a live fallback-image defect. Original URL/CDN response, accurate image content/rights, actual upload/replace/clear and correct rendering still require verification. The blank nine-concept draft is not a map of current production assets. |
| Legacy PDF/fulfilment | Actual intended row and obligations reviewed; verified fulfilment or approved withdrawal preserving history. No production withdrawal is claimed. |
| Live browser/security/SEO | Selected-revision desktop/mobile navigation, forms, auth, private pet/blog CRUD and order privacy, cart, image fallbacks, HTTPS/security configuration, robots/sitemap and persistence. Owner-verified public shop/cart success is recorded above; other screenshots/checks remain local and broader deployed acceptance is unverified. |
| Assessment/submission | Final check against the owner's issued full guide, correct repository/site links and genuine redacted evidence. No Pass is guaranteed. |

**Current decision:** deployment/build/migrations and one owner-verified sandbox success are complete. The live product-image defect and unverified remaining acceptance prevent a claim of complete submission readiness. No missing-asset diagnosis or new public maintenance state is invented. This documentation change does not disable Maintenance Mode, enable payments, modify production or authorise any new deployment/provider action. See [remaining owner checklist](../OWNER_RELEASE_CHECKLIST.md), [configuration/acceptance matrix](../RENDER_CHECKLIST.md) and [testing record](../TESTING.md).
