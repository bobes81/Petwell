# Review and release gates for draft PR #9

This branch introduces `Product.is_available` (default `True`) and guards public catalogue, direct add-to-cart, cart display, Buy Again and checkout. It preserves order history. **The legacy PDF is NOT automatically archived.** Until an authorised operator explicitly marks the correct database row unavailable, it remains purchasable if payment is configured. Do not treat merging this code alone as resolving fulfilment.

## Checks completed by code inspection

- The cart template now displays an unavailable line without displaying a payable price and retains its Remove form.
- Checkout rejects an unavailable product in a stale session cart before Stripe Session creation.
- Existing paid OrderItem references remain intact and Buy Again excludes withdrawn items.
- The migration adds a default-true flag, so historical physical products remain available.
- Regression tests cover catalogue visibility, direct add-to-cart, stale cart removal, checkout validation, archived order history and migration default.

## Outstanding independent verification (not claimed passed)

1. GitHub CI: `python manage.py check`, `makemigrations --check --dry-run`, Django tests on SQLite/PostgreSQL 16/18, and production deployment checks. Review actual run results before merge.
2. Validate the migration on an isolated restored database, especially preserving existing 10 products, five orders, five order items, blog and subscriber records. Do not run against production during review.
3. Confirm the exact legacy PDF row by **name and actual database identity**, check any pending/paid orders or existing Stripe Sessions, and decide fulfilment/withdrawal. Do not guess IDs or silently delete.
4. Following backup and owner approval, migrate and explicitly set only the verified non-deliverable product `is_available=False` in Django admin; verify catalogue, stale cart, direct POST, reorder and checkout on deployed revision.
5. Never enable live payments or merge PR #9 automatically. Review CI and pending-payment state first.

PR #9 is intentionally a draft against `fix/pp5-resubmission`, not a production release. If Codex continues working on PR #8, reconcile both branches carefully before any merge.

## Additional pre-Codex code review (29 October 2026)

- The cart now blocks the checkout navigation link when **any** line is withdrawn, missing, or nonpositively priced, even when other payable items remain. The checkout endpoint independently rejects the stale cart; hiding the link is a UX guard, not a security boundary.
- Direct add-to-cart and public catalogue also reject nonpositive-priced items; tests added for direct POST, catalogue and mixed cart cases.
- Removed a redundant second product query in the add-to-cart handler.
- These commits were saved on this **draft** branch only. The GitHub commit-workflow lookup returned no pull-request workflow runs at the time of review; this is **not** evidence of passing or failing tests. Confirm CI via GitHub Actions, then run the full SQLite and PostgreSQL suites before any release.
- **Operational blocker remains:** the old PDF record defaults to available until an authorised operator verifies its identity and explicitly withdraws it. Never automatically update a guessed product row or remove historical orders.
