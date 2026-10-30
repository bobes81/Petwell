# Owner-reported real-data rehearsal — 29 October 2026

**Source and scope:** the project owner's report supplied on 29 October 2026. The repository reviewer did not connect to the Mac database, repeat these operations or receive raw database output/screenshots. This is a dated record of the owner's manual results, not an automated test log or independent provider verification. No backup, credentials, record identifiers or customer content are included.

The owner restored the 28 October Render PostgreSQL backup into an isolated PostgreSQL 18 working copy on their MacBook. The five pending project migrations (`accounts.0001` and `orders.0002`–`0005`) applied successfully, and Django reported no remaining migrations.

| Check reported by the owner | Result |
| --- | --- |
| Original products preserved | 10 |
| Original orders preserved | 5 |
| Original order items preserved | 5 |
| Original blog posts preserved | 2 |
| Original subscribers preserved | 2 |
| Orders missing public UUIDs | 0 |
| Duplicate public UUIDs | 0 |
| Missing order links | 0 |
| Legacy orders incorrectly marked paid | 0 |
| Local shop and cart | Passed |
| Unavailable-payment protection | Passed |
| Signup, login and logout | Passed |
| Private pet-profile CRUD | Passed |
| Blog CRUD | Passed |
| New user's order history | Passed: empty |

This completes the owner-reported restored-copy migration, integrity and listed local-browser rehearsal. Do not require repeating this completed work merely because it was not run by the repository reviewer.

It does **not** establish a production deployment or migration, a successful Stripe payment/webhook delivery, a Cloudinary upload, SMTP delivery, authorised product-image rights or complete accessibility/cross-browser acceptance. No payment was claimed in this report; the unavailable-payment result verifies protection when provider actions are disabled.

The production release remains subject to the [Render gates](../RENDER_CHECKLIST.md) and [cutover/recovery runbook](../RELEASE_RUNBOOK.md), including a fresh release-time backup, checking for changes since this rehearsal and explicit approval. Keep private raw evidence locally if needed for assessment; do not publish customer records or the database dump.
