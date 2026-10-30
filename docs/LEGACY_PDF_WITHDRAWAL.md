# Exact-record legacy PDF withdrawal

Prepared 29 October 2026. The owner conditionally approved withdrawing **Mindful Pet Journal (PDF)** if it is confirmed to be the undeliverable historical offer. This is not approval to access/write production now. No production record was identified or changed by this review.

## What the command does

`review_legacy_pdf` defaults to read-only JSON discovery of the **exact name**, never a guessed ID or fuzzy match. It reports availability, price, hashed description/image reference, a snapshot fingerprint and aggregate historical order/checkout counts. It excludes customer details, order UUIDs, Session IDs and raw descriptions/images. Keep even this record review private.

Application requires an explicit positive product ID, the unchanged reviewed fingerprint and three owner attestations. Inside a transaction it locks the selected product and changes **only `is_available=True` to `False`**. It never deletes/reactivates records, changes images/prices/descriptions, changes orders or contacts a provider. A version-only Cloudinary image change invalidates the fingerprint. A repeated unchanged application reports `ALREADY_WITHDRAWN` with no update. An active checkout lease blocks the first withdrawal.

The fingerprint deliberately excludes availability to allow that no-op repeat. It is a stale-record guard, not proof of identity, deliverability, checkout pause or rights. Duplicate exact-name rows are reported without choosing one. A missing/renamed record or changed fingerprint requires a fresh private investigation, not relaxed checks.

## Future owner-reviewed procedure — after deployment and migration

Use the [30 October cutover plan](RELEASE_2026-10-30.md). All commands below must run from the **approved new revision**, with `petwell.settings`, against the privately verified intended database. Use an already available Render Shell only if genuinely supported; otherwise use the owner's MacBook and existing approved connection procedure. Do not buy a shell/service. Before access, obtain the required explicit production-access/write approval. Never paste connection values or reports into Git/chat.

1. Confirm the new code and all migrations, particularly `products.0002`, are active. Confirm the fresh recoverable backup, approved all-writer pause and drained requests. Migration defaults the PDF to available; it does not identify or withdraw it. Do not seed production.
2. Discover candidates **without writes**:

   ```bash
   python manage.py review_legacy_pdf --settings=petwell.settings
   ```

3. Privately inspect the actual row in read-only admin/detail review: exact name, description, price, image/reference, historical item links and any delivery promise/file. Confirm it is the undeliverable historical offer. Names/hashes alone do not establish that. If none/multiple/uncertain, stop and identify the correct row; never guess a database ID or withdraw every match.
4. Narrow the report with the actual reviewed ID:

   ```bash
   python manage.py review_legacy_pdf --product-id ACTUAL_REVIEWED_ID --settings=petwell.settings
   ```

   Replace the uppercase placeholder; it is not a runnable ID. Keep its `snapshot_fingerprint` privately. Independently compare historical pending/paid orders, saved unmapped attempts, active leases and any issued hosted Sessions against authorised provider records. Aggregate counts are warning information, not clearance. Resolve existing delivery obligations separately; do not erase history or falsely promise delivery. Do not automatically expire/refund Sessions or mark any order paid. Pausing the site does not invalidate hosted payment URLs.
5. Have the owner review the exact row/fingerprint, absence of in-flight creation, external reconciliation and write permission. Only when all three attestations are true, replace both placeholders and apply:

   ```bash
   python manage.py review_legacy_pdf --product-id ACTUAL_REVIEWED_ID \
     --expected-fingerprint ACTUAL_REVIEWED_SHA256 \
     --confirm-undeliverable --checkout-paused --orders-reviewed --apply \
     --settings=petwell.settings
   ```

   These flags record the operator's attestations; the command cannot verify the pause or provider state. A refusal means stop and investigate, not bypass the guard. Do not use a full stale admin edit form as a shortcut: it could overwrite unrelated fields.
6. Require `APPLIED` (or `ALREADY_WITHDRAWN` on a deliberate repeat), rerun step 4 read-only and confirm availability is false. Compare product fields, historical order/item counts and links privately with the before record. Verify catalogue exclusion, rejected direct add POST, stale-cart warning/removal and no re-add via Buy Again. Historical orders must still render. Existing valid signed payments may still be recorded; withdrawal is not a provider transaction barrier. Keep checkout unavailable until acceptance/reconciliation and reopening are separately approved.

## Repository evidence and limits

[Command](../products/management/commands/review_legacy_pdf.py), [synthetic command tests](../products/test_pdf_withdrawal.py), [availability regression matrix](LEGACY_PDF_REGRESSION_MATRIX.md) and [current test record](TESTING.md). Tests cover read-only discovery, duplicates, missing approvals, stale/versioned snapshots, history preservation, conflict rollback, active leases and repeat no-op. They do not identify the actual production PDF or execute withdrawal there. Do not reverse the availability migration to undo a withdrawal: that discards flags and can reopen the offer.
