# PR #8 review — 27 October 2026

Reviewed [PR #8](https://github.com/bobes81/Petwell/pull/8), branch `fix/pp5-resubmission`, starting at `b77fb811ddb30e4253edc251d807b6007914bf45`. The original 46 tests passed, as did the existing GitHub workflow. No original test failure was hidden or disabled; review found missing regression coverage.

## Findings fixed

| Finding | Failure scenario | Fix and regression coverage |
| --- | --- | --- |
| Mutable Stripe retry parameters | Stripe receives a create request, the response is lost, then a product is renamed or the cart key order changes. Retrying the same key rebuilt different parameters and Stripe rejected it. | Save the exact create payload before the network request; retry it unchanged. Freeze product labels and canonical line order. |
| Expired checkout loop | A cancelled/abandoned Session expires. Replaying its create request can keep redirecting to an unusable cached Session. | Retrieve saved Sessions; reuse open URLs, await webhook for completed Sessions, renew confirmed expired Sessions with a fresh order/key. Also recover from an expired cached create response. Keep old mappings. |
| Possible new item loss | A product is removed and re-added before the old payment webhook arrives; quantity-only clearing deleted the new line. | Per-line identities are captured with the order and reset on removal. Clear only purchased quantities from the matching original line. |
| Checkout without webhook configuration | API credentials were present but the signing secret was absent, so payment could start without local confirmation being configured. | Require both keys before creating a Session. Preserve the cart and show a useful error otherwise. |
| Payable/paid order deletion | Admin deletion could orphan an outstanding Session or destroy a paid history record. | Disable order deletion, including for superusers through admin. Payment/snapshot fields remain read-only. |
| Legacy retry cannot be reconstructed safely | Pre-fix pending order has neither saved payload nor Session ID after a lost response. | Start a fresh order/key; preserve the old row instead of guessing its original idempotent request. |
| Malformed payment input | Signed malformed JSON structures or missing mode/metadata could cause a server error or incomplete validation. | Reject malformed events and missing explicit live/test mode. Verify stale-signature rejection. |
| Missing Cloudinary name causes server errors | Stored images accessed `.url` while optional Cloudinary configuration was absent; browser `onerror` could not catch server-side URL construction. | Shared safe image URL filter and form widget use local placeholders; retain/clear/text-edit flows still work. |
| Newsletter database length error | A syntactically valid email exceeded the model's 254-character field; PostgreSQL could fail although SQLite accepted it. | Validate with a form using the model field's length before persistence. Preserve normalization and duplicate handling. |

The payment payload and cart-line snapshots contain no API or webhook secrets. They are protected read-only fields in admin. Migration `0004` adds the snapshots with empty defaults; it does not invent payment evidence. Legacy paid orders with no line identities do not automatically remove cart items, because the original line association cannot be established safely.

## Validation actually performed

- **63 Django tests passed**, no failures or skips. Includes the original suite, 17 added regressions, signed webhook verification, pending/paid behavior, cart safety, blog author/staff permissions, image handling, migration safety and order history privacy.
- Two new tests were run against the original code and failed as expected (mutable retry payload and removal/re-add cart loss). [Original regression failures](evidence/pr8-regressions-before.txt) and [final test output](evidence/django-tests.txt) are retained.
- Django system and migration consistency checks passed. Local `build.sh` installation, manifest static collection and migration `0004` succeeded.
- `check --deploy --fail-level WARNING` passed with production-style settings and an ephemeral strong local secret. This does not validate the actual Render configuration. The development fallback secret remains unsuitable for deployment.
- Local Gunicorn/WhiteNoise smoke requests passed for eight public routes and the page's manifest assets, HSTS, HTTP-to-HTTPS redirect, Render sitemap URLs and refusal of an unconfigured webhook. [Machine-readable results](evidence/pr8-production-smoke.json). This uses SQLite and a trusted-proxy header on loopback; it is not a Render, external TLS or PostgreSQL integration test.
- Updated CI to run production-style system checks and static collection as well as the existing Django suite. Check the current PR head's run before merging.

No Stripe API calls, payment processing, external Cloudinary uploads or SMTP sends were performed. Stripe calls and upload operations in automated tests are mocked; signature verification uses the real verifier with a fixture signing secret. Browser screenshots linked in TESTING.md belong to the earlier implementation and are not newly captured deployed evidence.

## Remaining before merge/deployment

1. Review the supplied Code Institute rubric and assessor feedback against these fixes. A passing test suite does not establish an assessment Pass.
2. Configure the real Render environment securely: strong `SECRET_KEY`, `DEBUG=False`, correct host/`SITE_URL`, persistent PostgreSQL `DATABASE_URL`, Stripe **sandbox** API/signing keys, Cloudinary configuration and verified SMTP sender if delivery is required. None of these credential bindings is present in this cloud instance.
3. After an explicitly approved deployment to the intended test environment, run a real Stripe sandbox checkout and verify matching webhook delivery and paid order. Verify decline, cancellation, completed-before-webhook, duplicate delivery and delayed cart reconciliation. Never enable live mode or use a real card for this assessment check.
4. Run actual Render deployment checks, verify database persistence/backups and apply migrations including `0004`. Confirm successful webhook delivery for both subscribed Session events. Check real Cloudinary uploads and password-reset email delivery. Review legacy orders/carts without guessing past payment status.
5. Complete the deployed responsive, accessibility, validator and cross-browser matrix; add genuine wireframes, screenshots, source credits and Facebook marketing evidence. [Evidence checklist](EVIDENCE.md).

PR remains unmerged. No production deployment, live payment enablement or payment was performed by this review.
