# Owner-controlled release and recovery runbook

Prepared on 28 October 2026. **Current release decision: NO-GO until the outstanding gates in [RENDER_CHECKLIST.md](RENDER_CHECKLIST.md) are verified and the owner explicitly approves the exact release.** This document is a plan, not evidence that a deployment, backup, restore, payment or external check occurred. No production access or service change was performed to prepare it.

## Starting point and required preparation

The owner confirms applied `orders.0001_initial`, `products.0001_initial` and the complete `blog.0001`–`blog.0004` history, including both conflicting branches and the merge. The new `orders.0002`–`0005` and `accounts.0001_initial` are not yet applied. Other installed applications' migration records and the actual schema must still agree with the reviewed forward plan; this repository review did not inspect production.

Before a later approved release, record the selected commit, successful SQLite/PostgreSQL CI, private backup reference and recovery verification, full applied/pending migration labels, existing service cutover method, and the owner's approval. Keep configuration values, connection strings, reset links and customer information out of Git and public evidence. Reuse existing resources; this plan does not require a paid plan, new service or secret rotation.

Arrange a maintenance/write-pause method using the existing service's available controls, and verify it before migration. The pause must cover every process capable of writing to the database, not just the browser checkout button. Old workers cannot insert orders after the required new order fields are added. `build.sh` applies migrations during build, so it is a write operation and cannot serve as a read-only readiness check. A pre-deploy migration command does not remove the need to coordinate old writers and code cutover.

## Forward release or abort

| Observed stage | Safe decision for the owner after explicit release approval |
| --- | --- |
| Before any production migration or other release write | If a gate fails, abort the release and retain the existing code/database pair. Do not run the build or migration command as a diagnostic shortcut. |
| A migration fails | Keep the write pause. Preserve the exact failure and complete applied/pending history privately; sanitise any public report. PostgreSQL atomicity is per migration, so earlier successful migrations can remain applied even when the overall command fails. Review the actual state before choosing a forward fix or recovery. Do not delete migration records, fake application or assume the whole batch rolled back. |
| Migrations succeed but the new app is unhealthy | Keep the pause and prefer a reviewed forward fix that understands the new schema. Do not switch order-writing traffic back to the old revision. Reversing `orders.0002`–`0005` removes payment fields, request snapshots and the coordinator; reversing `accounts.0001` removes pet profiles. A blind schema downgrade is not a safe rollback. |
| New app and schema are healthy | Perform approved sandbox/external acceptance before reopening normal writes. Confirm the selected code is actually serving, all workers use it, migrations are complete, HTTPS/static/auth paths work, and order/payment/privacy checks pass. Record genuine outcomes with dates and commit identifiers. |

Do not run `products.seed.run()` against production as part of release or recovery: it changes catalogue records and cannot substitute for reviewing the existing products and authorised photos. Do not manually relabel legacy orders paid; migration intentionally leaves orders without Stripe evidence pending.

## Restoring a database is a separate recovery decision

A database restore replaces data written after its snapshot. Before any approved restore, preserve the current recovery state privately and determine whether new orders, users, posts, subscribers, pet profiles or other accepted writes exist. A backup existing is not proof that restoring it is safe. Select matching application code and verify recovery against the restored migration history before allowing writes.

Stripe state also exists outside the database. Pausing PetWell does **not** invalidate an already issued hosted Checkout URL. A Session may complete while the application is paused, and a signed event may arrive later. Restoring an older snapshot can remove the order UUID, exact item prices, frozen request payload, Session mapping or paid state needed to validate that event. The webhook correctly requests retry for an unknown Session; retries alone cannot reconstruct lost order records.

If any checkout could have been issued or any payment accepted since the backup:

1. Keep checkout/order writes paused. Do not assume an empty local paid-order list proves there are no provider payments or still-payable Sessions.
2. Under separately approved sandbox/provider access, reconcile all affected Sessions, payments and delivered/pending events against preserved order records and the backup interval. Confirm or close outstanding payable attempts through an approved provider procedure before allowing replacements. Unknown or ambiguous states remain blocked.
3. Recover and verify the original order/item/Session mappings and reconcile accepted post-backup writes before resuming. Do not manufacture replacement identifiers, create a second Checkout attempt because a mapping disappeared, mark paid from a return page/screenshot, or bypass signed validation. Do not initiate refunds, cancellations, live payments or other financial actions without their required explicit approval.
4. Repeat genuine signed-event acceptance and duplicate/retry/cart-reconciliation checks on the recovered matching code/database pair. Keep an accurate private reconciliation record; public evidence must exclude secrets and personal/payment identifiers as appropriate.

Only a verified absence of post-backup writes **and** external payment/session changes can support the simple matching-backup/code recovery path. Otherwise, recovery needs an approved preservation/reconciliation plan; keep the release NO-GO until that plan is complete. A database backup does not roll back changes in Cloudinary, email delivery or Stripe.

## Acceptance and evidence boundaries

The signed sandbox destination is `https://petwell-u0cr.onrender.com/checkout/webhook/`, receiving `checkout.session.completed` and `checkout.session.async_payment_succeeded`. Use the same test account for the API key and endpoint signing secret, keep `STRIPE_LIVE_MODE=False`, and never use real card data. Local mocked API tests and signed fixture tests do not establish actual provider delivery.

After an approved release/recovery, record actual test success, decline/cancel, duplicate/delayed webhook handling, private order history, blog permissions, pet CRUD, Cloudinary upload and received password-reset email results. The catalogue still needs accurate authorised photographs and source records; any offered PDF needs a verified fulfilment process. Clearly labelled local design mockups and historical local screenshots remain separate from deployed/external evidence.

See [TESTING.md](TESTING.md) for the tests actually run, [EVIDENCE.md](EVIDENCE.md) for submission evidence gaps and [ASSETS.md](ASSETS.md) for image requirements. Reversing schema inside a disposable migration regression is test setup only, never this runbook's production recovery instruction.
