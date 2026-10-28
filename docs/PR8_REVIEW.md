# PR #8 resubmission review — 28 October 2026

Continued from `166334a` on the same `fix/pp5-resubmission` branch, preserving its previous payment/blog fixes. The earlier 63-test baseline passed; this review added uncovered failure cases and the additional distinct custom feature. The owner's private assessment correspondence is not published. The project-level mapping is in [ASSESSMENT_REVIEW.md](ASSESSMENT_REVIEW.md).

## Changes completed

- **Distinct custom model and frontend:** `PetProfile` provides member-owned species/care-focus/notes, routine reminders and full validated CRUD at `/pets/`. Owner-only queries prevent direct access by other members or staff; no medical claim is made.
- **Duplicate-payment safety:** resolve the existing Stripe attempt before reacting to changed cart/contact data. Completed sessions wait for webhook confirmation. Superseded open sessions must be confirmed expired before replacement; ambiguous failures keep the old attempt. `CheckoutState` provides a durable pointer and token-checked 120-second database lease without holding a database transaction over Stripe I/O. Requests have a bounded 10-second Stripe timeout.
- **Recovery:** stale browser workers reuse the durable pointer; worker/lease takeover cannot overwrite a newer holder; same-session confirmation ownership can be recovered after lost session data. Frozen request snapshots and old Session mappings remain intact. Only signed webhook validation can mark paid.
- **Account UX/security:** preserve validated internal destinations across login/signup; reject external redirects; explain invalid/expired/sessionless/used password-reset links and offer recovery.
- **SEO/navigation:** distinct escaped metadata, trusted public canonicals without query strings, private noindex, correct Render crawler URLs/copies, My pets navigation and complete heading outlines. Old settings module now aliases the authoritative current configuration instead of restoring retired hosts.
- **Assets/design:** factual image inventory; no unrelated/generated title cards passed off as product photos. New Facebook-page mockup is explicitly not published. New wireframes are dated retrospective design review. Both have genuine local renders. ERD reflects actual models; feature stories separate code/testing from deployed completion.
- **Validation:** moved invalid body style blocks into scoped CSS while preserving appearance; added markup regression and genuine Nu HTML/CSS outputs. Added PostgreSQL CI coverage for lease concurrency.

## Checks actually completed

- SQLite Django suite: **108 tests, 107 passed, 1 explicit PostgreSQL-only skip, 0 failures**. Actual output: [django-tests.txt](evidence/django-tests.txt). No assertion was removed or disabled for a pass.
- Local mobile/desktop Chromium: **10 grouped flows, 16 screenshots**, no detected overflow/broken images/external requests/JavaScript exceptions in checked states; blog CRUD/permissions, pet CRUD/validation/privacy, synthetic history/reorder, auth recovery and unavailable checkout all passed. [Browser results](evidence/28oct-browser-results.json).
- Nu checker: **19 HTML documents and 2 project CSS files**, no messages on the final runs. Optional strict style audit failures are separately disclosed in [TESTING.md](TESTING.md); no false style/all-accessibility pass is claimed.
- Build, migrations, dependency consistency, system checks, production-style settings and local Gunicorn/WhiteNoise smoke checks passed. This is not actual Render, external TLS or PostgreSQL integration validation.
- CI is configured for SQLite plus PostgreSQL 16. The local PostgreSQL-only test is skipped because no local server is available; verify the actual current head's CI status rather than infer it from SQLite.

All repository/PR text is English. Common credential shapes, private-correspondence copying, whitespace, relative documentation links and final app diffs were reviewed. Fixture passwords, synthetic users and manually seeded paid orders are test data; they are not external payment evidence.

## Migration/release review

Back up the existing database; run `python manage.py showmigrations` and `python manage.py migrate --noinput` with the approved configuration. In addition to earlier migrations, `accounts.0001` creates PetProfile and `orders.0005` creates CheckoutState. Do not fake or edit applied migrations. Legacy orders without Stripe evidence remain pending; old cart lines without provable identity are not removed automatically.

No merge, deployment, live mode, real payment, external upload/email or new production service was performed. The deployment target is `https://petwell-u0cr.onrender.com`; this branch is not claimed to be live.

## Owner actions before submission

1. Review the actual assessment guide against the evidence map; approve the completed branch only after remaining mandatory gaps are checked. No Pass is guaranteed.
2. Supply accurate authorised catalogue photos/source records. Current fallbacks are usable but are not real product photographs.
3. Configure/reuse secure Render/PostgreSQL, Stripe **sandbox**, Cloudinary and verified SMTP bindings; review backups/migrations and explicitly approve the test deployment. Never put keys in chat, Git or screenshots.
4. After approved deployment, complete a real sandbox payment and signed webhook acceptance, decline/cancel/retry checks, upload/email and database-persistence verification, and deployed accessibility/browser evidence.
5. Apply the saved `api.github.com` network requirement to the cloud runtime if direct PR-description/issue administration is needed. Native Git can update this PR branch, but direct GitHub API is currently blocked. Feature-level issue drafts/statuses are documented honestly in [USER_STORIES.md](USER_STORIES.md); no invented issues or sprint history are claimed.

A clearly labelled Facebook mockup and retrospective design artifacts are included; they are not live marketing or original historical planning. The main remaining submission gaps are genuine product photos and actual approved-deployment/integration evidence, plus final assessment-guide review.
