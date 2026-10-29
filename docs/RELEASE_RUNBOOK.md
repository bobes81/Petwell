# Owner-controlled release and recovery runbook

Prepared on 28 October and updated on 29 October 2026. **Current release decision: NO-GO until the outstanding gates in [RENDER_CHECKLIST.md](RENDER_CHECKLIST.md) are verified and the owner explicitly approves the exact release.** This document is a plan. The owner's separately reported successful restored-copy migration/browser rehearsal is recorded below; it is not a claim that this review deployed, restored production, processed a payment or verified external integrations. No production access or service change was performed to prepare it.

## Starting point and required preparation

The owner confirms applied `orders.0001_initial`, `products.0001_initial` and the complete `blog.0001`–`blog.0004` history, including both conflicting branches and the merge. The new `orders.0002`–`0005` and `accounts.0001_initial` have been applied successfully to the owner's isolated working copy, but remain reported pending in production. Other installed applications' migration records and the actual schema must still agree with the reviewed forward plan; this repository review did not inspect production.

Before a later approved release, record the selected commit, successful SQLite/PostgreSQL CI, private backup reference and recovery verification, full applied/pending migration labels, existing service cutover method, and the owner's approval. Keep configuration values, connection strings, reset links and customer information out of Git and public evidence. Reuse existing resources; this plan does not require a paid plan, new service or secret rotation.

Arrange a maintenance/write-pause method using the existing service's available controls, and verify it before migration. The pause must cover every process capable of writing to the database, not just the browser checkout button. Old workers cannot insert orders after the required new order fields are added. `build.sh` applies migrations during build, so it is a write operation and cannot serve as a read-only readiness check. A pre-deploy migration command does not remove the need to coordinate old writers and code cutover.

## Restored-copy migration and browser rehearsal completed

On **29 October 2026**, the owner reported successful restoration of the 28 October Render backup into an isolated PostgreSQL 18 working copy, application of **all five pending project migrations**, and **no remaining migrations**. Original records were preserved: **10 products, 5 orders, 5 order items, 2 blog posts and 2 subscribers**. The reported integrity checks found **zero missing UUIDs, duplicate UUIDs, missing order links or incorrectly paid legacy orders**. [Dated owner-reported results and scope](evidence/29oct-owner-rehearsal.md).

The owner also reported passing local browser checks for shop, cart, unavailable-payment protection, signup, login/logout, private pet CRUD, blog CRUD and empty order history for a new user. This is owner-performed, real-data local rehearsal evidence; the repository review did not access the database or independently repeat those checks. No customer records, database dump, credentials or private screenshots are published. The rehearsal does not establish Stripe, Cloudinary, SMTP or deployed acceptance, and does not claim checks beyond the owner's list.

**The restore/forward-migration/local-browser gate is completed; do not repeat it as an outstanding task.** Preserve the original backup and genuine private results. [The local-only procedure](RESTORED_DB_REHEARSAL.md) remains available as a record and for a future relevant schema change. Repository-only tests remain separate and use disposable synthetic databases. A later schema change or evidence of production drift would justify a targeted new rehearsal, rather than rerunning completed checks by default.

A restore onto PostgreSQL 18 does not establish the production server version or prove an in-place production upgrade. Before a later approved release, confirm the actual target/version, release-time backup and accepted writes since the 28 October snapshot. The external-payment reconciliation requirements below still apply.

## Smallest approved cutover sequence

These are future owner-controlled production actions, **not permission to perform them now**. Keep the existing deployment resources and select a method the current service actually supports; do not upgrade a plan or create a service to follow this checklist.

1. **Select and approve the release.** Record the exact reviewed PR head and green SQLite/PostgreSQL CI. Confirm existing Render auto-deploy behaviour before any merge/push intended to release; merging and deploying remain separate approval decisions. Privately verify the production target/version, full migration/schema agreement and necessary service bindings. A green isolated rehearsal does not prove the current production state.
2. **Pause writers before any migrating build.** Record the actual existing-service method that stops all old workers, admin/tasks and request paths capable of writes. If that method is unavailable or cannot be verified, stop the cutover; do not use an upgrade or an unverified zero-downtime assumption. Account for still-payable Stripe URLs and delayed webhooks as described below. After the write boundary, take and privately verify a fresh backup covering accepted writes since 28 October. Retain the original backup too.
3. **Apply the selected code/schema pair once.** With the pause maintained, inspect `showmigrations` and `migrate --plan` using approved production settings. The expected new project migrations are `orders.0002`–`0005` and `accounts.0001`; stop on an unexpected plan. The existing `bash build.sh` installs dependencies, collects static files **and applies migrations**. If using that existing build, migration is part of the approved cutover, not a readiness probe. If an already available separate migration/pre-deploy stage is selected, use `python manage.py migrate --noinput` there and treat the build/stage arrangement as one reviewed procedure; both choices still require the pause. Do not fake or reverse migration records.
4. **Verify before reopening normal writes.** Confirm the selected revision is serving on all workers, `python manage.py migrate --check` reports no pending migrations, and `python manage.py check --deploy --fail-level WARNING` passes. Compare preserved original counts/links/state privately against the fresh backup, allowing only documented deliberate test additions. Verify HTTPS/static/auth/private pet/blog/order paths. Run actual sandbox/provider acceptance only with its separately required approval and safe test data; record what was and was not verified.
5. **Choose resume or abort.** Reopen normal writes only after the owner accepts the observed results and provider/reconciliation gaps are resolved. On failure, keep the pause and use the stage table below. A new-code health failure after migration does not make old-code writes or blind schema downgrade safe.

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
