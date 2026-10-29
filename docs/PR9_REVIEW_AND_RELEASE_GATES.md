# Review and release gates for draft PR #9

This branch introduces `Product.is_available` (default `True`) and guards public catalogue, direct add-to-cart, cart display, Buy Again and checkout. It preserves order history. **The legacy PDF is NOT automatically archived.** Until an authorised operator explicitly marks the correct database row unavailable, it remains purchasable if payment is configured. Do not treat merging this code alone as resolving fulfilment.

## Checks completed by code inspection

- The cart template now displays an unavailable line without displaying a payable price and retains its Remove form.
- Checkout rejects an unavailable product in a stale session cart before Stripe Session creation.
- Existing paid OrderItem references remain intact and Buy Again excludes withdrawn items.
- The migration adds a default-true flag, so historical physical products remain available.
- Regression tests cover catalogue visibility, direct add-to-cart, stale cart removal, checkout validation, archived order history and migration default.

## Remaining release verification

1. Verify the exact reviewed head's SQLite/PostgreSQL 16/18 GitHub CI and production-style checks. Local results are recorded below; they do not establish actual Render or provider acceptance.
2. The owner already completed the five earlier migrations/integrity/browser rehearsal. Rehearse only the new `products.0002_product_is_available` on a disposable copy of that already-migrated local database; verify original 10 products, five orders/items, blog/subscribers and existing flags. Do not repeat the completed backup restore unnecessarily or run against production during review.
3. Confirm the exact legacy PDF row by **name and actual database identity**, check any pending/paid orders or existing Stripe Sessions, and decide fulfilment/withdrawal. Do not guess IDs or silently delete.
4. Following backup and owner approval, migrate and explicitly set only the verified non-deliverable product `is_available=False` in Django admin; verify catalogue, stale cart, direct POST, reorder and checkout on deployed revision.
5. Never enable live payments, merge into production `main` or deploy without owner approval. The latest owner request explicitly authorises reconciling this reviewed feature branch into PR #8; that does not authorise a release.

PR #9 is intentionally a draft against `fix/pp5-resubmission`, not a production release. If Codex continues working on PR #8, reconcile both branches carefully before any merge.

## Additional pre-Codex code review (29 October 2026)

- The cart now blocks the checkout navigation link when **any** line is withdrawn, missing, or nonpositively priced, even when other payable items remain. The checkout endpoint independently rejects the stale cart; hiding the link is a UX guard, not a security boundary.
- Direct add-to-cart and public catalogue also reject nonpositive-priced items; tests added for direct POST, catalogue and mixed cart cases.
- Removed a redundant second product query in the add-to-cart handler.
- These commits were saved on this **draft** branch only. The GitHub commit-workflow lookup returned no pull-request workflow runs at the time of review; this is **not** evidence of passing or failing tests. Confirm CI via GitHub Actions, then run the full SQLite and PostgreSQL suites before any release.
- **Operational blocker remains:** the old PDF record defaults to available until an authorised operator verifies its identity and explicitly withdraws it. Never automatically update a guessed product row or remove historical orders.


## Independent repository review and tests — 29 October 2026

The reviewer fetched the actual PR #8 head `846f2fb` and draft PR #9 head `b39ec91`; the latter descends from the former. No existing commits were discarded or duplicated. PR #9's original SQLite baseline passed **164 tests: 163 passed, 1 PostgreSQL-only skip**: [actual output](evidence/29oct-pr9-baseline-tests.txt).

The review found misleading Buy Again feedback: the page reported items added even if all order items were withdrawn. Two new regressions reproduced that message failure before the fix. Feedback now distinguishes an actual addition, skipped unavailable/unpriced items and no cart additions, preserving the existing cart and historical purchases.

Eight new regressions cover guest/member checkout POSTs for withdrawn/missing/zero/negative-priced products (no order, lease or Stripe request), missing mixed-cart recovery, mixed and fully unavailable reorder, negative-price catalogue/direct POST, re-seeding without reactivation, a targeted schema upgrade and signed confirmation for a Session issued before withdrawal. Last case preserves genuine payment evidence; a database flag cannot invalidate an already-issued hosted URL.

**Reviewed SQLite suite: 172 tests, 171 passed, 1 PostgreSQL-only skip, 0 failures**: [actual output](evidence/29oct-pr9-reviewed-tests.txt). Django system checks and `makemigrations --check --dry-run` passed. Exact-head PostgreSQL 16/18 CI must be checked after push; these local results do not claim it in advance.

The new incremental migration fixture starts after the five owner-rehearsed migrations and requires exactly `products.0002`, preserving identities, fields, image/order links and pending state. Every existing product, including the PDF, defaults to available; **no unverified row is automatically withdrawn**. This preserves existing rows but is not permission to run old writers: the default is an application default, and an old Product writer fails after the required column is added. Coordinate the existing all-writer pause and code cutover, then verify the exact record before any separately approved archive action. No applied migration file was rewritten.

No production data, Stripe payment, provider upload/email, Render setting or paid resource was changed. The new availability migration is not covered by the earlier real-data rehearsal until the owner performs that one targeted check. Outstanding issued Sessions and fulfilment obligations require approved provider reconciliation; no automatic expiry or fabricated delivery was added.
