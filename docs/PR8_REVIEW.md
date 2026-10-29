# PR #8 resubmission review — 29 October 2026

This branch repairs checkout/payment confirmation and blog authorisation, supplies the distinct private PetProfile feature, and adds genuine local testing/design evidence for the PP5 resubmission. The owner's private assessment correspondence is not published; the project-level mapping is in [ASSESSMENT_REVIEW.md](ASSESSMENT_REVIEW.md).

The latest review follows `21e4c32`. The owner reports a successful isolated PostgreSQL 18 restore on their Mac with 10 products, 5 orders and 2 posts; this review did not access it or infer a successful forward migration. A new [local-only profile and owner procedure](RESTORED_DB_REHEARSAL.md) avoid production URL fallback, permit local PostgreSQL without forced SSL and disable provider actions. The confirmed migration fixture still preserves commerce/blog/subscriber data and applies only the five pending project migrations.

A genuine checkout recovery fix now holds a frozen but unmapped attempt after 23 hours, before assuming Stripe idempotency keys remain available indefinitely. It preserves the original order/cart/payload for reconciliation and leaves known Session retrieval unchanged. Three regressions reproduce the pre-fix duplicate-create risk and verify the hold/boundary/changed-data recovery. No application model or applied migration was rewritten.

**Release decision: NO-GO** pending the remaining configuration, backup/cutover, schema and genuine sandbox acceptance gates. The [Render checklist](RENDER_CHECKLIST.md) and [forward/abort/recovery runbook](RELEASE_RUNBOOK.md) explain those decisions; no production access, deployment or live payment is claimed.

## Changes completed

- **Distinct custom model and frontend:** `PetProfile` provides member-owned species/care-focus/notes, routine reminders and full validated CRUD at `/pets/`. Owner-only queries prevent direct access by other members or staff; no medical claim is made.
- **Duplicate-payment safety:** resolve the existing Stripe attempt before reacting to changed cart/contact data. Completed sessions wait for webhook confirmation. Superseded open sessions must be confirmed expired before replacement; ambiguous failures keep the old attempt. `CheckoutState` provides a durable pointer and token-checked 120-second database lease without holding a database transaction over Stripe I/O. Requests have a bounded 10-second Stripe timeout.
- **Recovery:** stale browser workers reuse the durable pointer; worker/lease takeover cannot overwrite a newer holder; same-session confirmation ownership can be recovered after lost session data. Frozen request snapshots and old Session mappings remain intact. Only signed webhook validation can mark paid.
- **Configuration compatibility:** existing `CLOUDINARY_URL` configures image rendering/uploads without separate variables; resolved storage configuration preserves SDK credentials and enforces HTTPS. Synthetic fresh-process tests cover native precedence and disabled unconfigured services.
- **Account UX/security:** preserve validated internal destinations across login/signup; reject external redirects; explain invalid/expired/sessionless/used password-reset links and offer recovery.
- **SEO/navigation:** distinct escaped metadata, trusted public canonicals without query strings, private noindex, correct Render crawler URLs/copies, My pets navigation and complete heading outlines. Old settings module now aliases the authoritative current configuration instead of restoring retired hosts.
- **Assets/design:** factual image inventory; no unrelated/generated title cards passed off as product photos. New Facebook-page mockup is explicitly not published. New wireframes are dated retrospective design review. Both have genuine local renders. ERD reflects actual models; feature stories separate code/testing from deployed completion.
- **Validation:** moved invalid body style blocks into scoped CSS while preserving appearance; added markup regression and genuine Nu HTML/CSS outputs. Added PostgreSQL CI coverage for lease concurrency.
- **Release safety:** confirmed-blog migration fixture checks no replay of applied blog/product migrations and preserves old records. Old-code order writes fail after the schema upgrade, so write pause/code cutover is required. Recovery must preserve/reconcile post-backup writes and issued Stripe Sessions rather than blindly restore or downgrade.

## Checks actually completed

- Latest SQLite Django suite: **125 tests, 124 passed, 1 explicit PostgreSQL-only skip, 0 failures**. [Actual complete output](evidence/29oct-django-tests.txt). Earlier runs remain preserved. No assertion was removed or disabled for a pass.
- New signed fixture tests confirm valid cookieless/CSRF-enforcing webhook delivery, wrong-signature rejection, browser-only cart reconciliation, async success and distinct/delayed success/failure/expiry/unpaid deliveries preserving paid state, timestamp and newly added cart lines. [Focused output](evidence/28oct-sandbox-webhook-followup-tests.txt). No Stripe API calls or external deliveries were made.
- Earlier local mobile/desktop Chromium: **10 grouped flows, 16 screenshots**, no detected overflow/broken images/external requests/JavaScript exceptions in checked states; blog CRUD/permissions, pet CRUD/validation/privacy, synthetic history/reorder, auth recovery and unavailable checkout all passed. [28 October results](evidence/28oct-browser-results.json).
- New 29 October targeted Chromium: desktop/mobile aged-attempt hold, cart/payload/pending state preserved and lease released; two genuine synthetic-data screenshots, no detected layout/JS/external-request issues and zero Stripe API attempts. [Actual report](evidence/29oct-aged-retry-browser-results.json). The owner's restored database was not used.
- Nu checker: **19 HTML documents and 2 project CSS files**, no messages on the final runs. Optional strict style audit failures are separately disclosed in [TESTING.md](TESTING.md); no false style/all-accessibility pass is claimed.
- Build, migrations, dependency consistency, system checks, production-style settings and local Gunicorn/WhiteNoise smoke checks passed. This is not actual Render, external TLS or PostgreSQL integration validation.
- CI is configured for SQLite plus PostgreSQL 16 and 18, including the migration/concurrency rehearsals. The original `postgres` check name remains for 16. Verify the exact current head's [PR checks](https://github.com/bobes81/Petwell/pull/8/checks); synthetic CI data is separate from the owner's restored copy.

Historical runs and previous browser/validator evidence retain their original scope and outputs in [TESTING.md](TESTING.md); the new screenshots cover only the aged-attempt hold, and no external validation was repeated. Latest local system/migration/deployment/dependency checks passed: [actual output](evidence/29oct-system-checks.txt). New [local profile probes](evidence/29oct-rehearsal-settings.txt) make no database connection, and the [before](evidence/29oct-aged-retry-before.txt)/[after](evidence/29oct-aged-retry-after.txt) retry logs use mocked Stripe calls.

All repository/PR text is English. Common credential shapes, private-correspondence copying, whitespace, relative documentation links and final app diffs were reviewed. Fixture passwords, synthetic users and manually seeded paid orders are test data; they are not external payment evidence.

## Migration/release review

Owner confirmation now includes both historical blog branches and the merge. Those files and the initial order/product migrations match `main`; none was rewritten. `orders.0002`–`0005` and `accounts.0001` remain pending. Verify the remaining installed-app history/schema and backup, then follow the approved write-pause/migration/code-cutover plan. Existing blog/subscriber rows are preserved; old orders without Stripe proof remain pending and old cart lines without identities are kept. A backup does not invalidate hosted Stripe URLs or reverse provider payments: preservation/reconciliation is required before any approved recovery. See the [runbook](RELEASE_RUNBOOK.md).

No merge, deployment, live mode, real payment, external upload/email or new production service was performed. The deployment target is `https://petwell-u0cr.onrender.com`; this branch is not claimed to be live.

## Owner actions before submission

1. Review the actual assessment guide against the evidence map; approve the completed branch only after remaining mandatory gaps are checked. No Pass is guaranteed.
2. Supply accurate authorised catalogue photos/source records. Current fallbacks are usable but are not real product photographs.
   Review the seeded PDF listing too: there is no implemented download-delivery feature. Provide and verify an actual fulfilment process or remove that listing from the offered catalogue before accepting payment for it.
3. Verify/reuse secure Render/PostgreSQL, the existing `CLOUDINARY_URL`, Stripe **sandbox** and verified SMTP bindings; review backups, outstanding migrations and write-pause/recovery plan, then explicitly approve the selected release. Never put keys in chat, Git or screenshots.
4. After approved deployment, complete a real sandbox payment and signed webhook acceptance, decline/cancel/retry checks, upload/email and database-persistence verification, and deployed accessibility/browser evidence.
5. Apply the saved `api.github.com` network requirement to the cloud runtime if direct PR-description/issue administration is needed. Native Git can update this PR branch, but direct GitHub API is currently blocked. Feature-level issue drafts/statuses are documented honestly in [USER_STORIES.md](USER_STORIES.md); no invented issues or sprint history are claimed.

A clearly labelled Facebook mockup and retrospective design artifacts are included; they are not live marketing or original historical planning. The main remaining submission gaps are genuine product photos and actual approved-deployment/integration evidence, plus final assessment-guide review.
