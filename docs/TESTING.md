# Test record — 28 October 2026

This record covers the current `fix/pp5-resubmission` work following `166334a`. It is not a production or external-service test report. The earlier 63-test baseline passed before this review; new tests were added for uncovered defects and the additional pet-profile feature. No failing assertion was disabled to obtain a pass.

## Automated checks actually run

```bash
python manage.py test --settings=petwell.test_settings --verbosity=2
python manage.py check --settings=petwell.test_settings
python manage.py makemigrations --check --dry-run --settings=petwell.test_settings
python -m pip check
```

**SQLite result: 108 discovered/executed tests — 107 passed, 1 explicitly skipped, 0 failures.** The skip is the PostgreSQL-only two-worker concurrency test. Deterministic stale-session, busy-lease, lease recovery/takeover, immutable-payload and payment-state tests run locally. Do not describe the SQLite run as proof of simultaneous PostgreSQL workers.

The test database is isolated and email is in memory. Stripe create/retrieve/expire and Cloudinary uploads are mocked; actual HMAC verification runs against signed fixture payloads. No test processes a payment, uploads an external image or delivers an email. [Actual local test output](evidence/django-tests.txt).

System checks, migration consistency and installed dependency checks passed. Selected Python error/import lint and whitespace checks passed. The repository changes were reviewed for English content, common real credential patterns, private-correspondence copying and broken relative documentation links; no matching accidental credentials/private text were found. Test passwords and the disposable CI PostgreSQL password are explicitly synthetic fixtures, not deployment credentials.

A further offline review resumed from `1f95d4b` on 28 October and changed documentation only. The full suite was rerun with the same result: **108 tests, 107 passed, 1 PostgreSQL-only skip, 0 failures**. System checks, migration consistency, production-style `check --deploy` (ephemeral local secret, no external services) and `pip check` passed again. [Follow-up test output](evidence/28oct-followup-django-tests.txt) and [review/CI record](evidence/28oct-followup-review.json) preserve this verification separately. Existing browser/validator screenshots and reports were reviewed, not recaptured or represented as new runs.

| Area | Meaningful regression coverage |
| --- | --- |
| PetProfile | Complete owner-only CRUD; owner assigned server-side; no access by another member/staff; CSRF; supported species/focus; required/overlong validation; escaped text; focus reminder |
| Blog | Author/staff CRUD; anonymous login requirement; direct non-owner GET/POST denial; GET delete confirmation; retained/cleared/new/invalid/oversized image; upload failure and absent Cloudinary configuration |
| Accounts | Signup/login, strong password checks, internal `next` retained across auth links, external redirects rejected, invalid/expired/sessionless/used reset links, successful reset via local email fixture |
| Payment creation | Database prices, bounded cart quantities, required API/signing keys, test/live mismatch rejection, frozen retries after lost responses/product rename/cart reordering |
| Payment lifecycle | Open/complete/expired Session states, expiry races/failure, changed data cannot bypass completed checkout, no replacement before old payable Session is closed, recoverable errors |
| Checkout coordination | Durable active-order pointer; preloaded stale worker requests deduplicated; busy lease refuses a second attempt; stale holder cannot overwrite/release a newer lease; interrupted holder releases safely |
| Signed webhooks | Valid signature and exact amount/currency/order/reference/mode; invalid/stale signature and malformed signed structures; duplicates; unpaid/unrelated events; late mapping retry; no return-URL payment confirmation |
| Cart/orders | Clear once only after confirmation; keep newly re-added lines/additional quantities; own history only; owner-only POST reorder at current prices; historical totals preserved; protected product/order deletion |
| SEO/markup | Render crawler URLs, public blog entries, private-page noindex and no canonical, trusted configured canonical host without query parameters, escaped metadata, public/form links and fallback images, complete heading outline and no body style blocks |
| Migrations | Distinct legacy UUIDs and pending status, safe migration round-trip to current orders schema; new pet/coordinator migrations detected and applied locally |

## Local browser/manual acceptance actually performed

Headless system Chromium through Playwright, desktop **1440×1000** and mobile **390×844**, isolated temporary SQLite, synthetic users/content. The final browser rerun followed the heading/CSS fixes and passed **10 grouped flows, 16 screenshots**, with zero external requests, JavaScript exceptions, detected horizontal overflow or broken images in the checked states.

[Machine-readable browser results](evidence/28oct-browser-results.json) provide the steps and screenshot captions.

| Feature | Steps and expected result | Actual local result |
| --- | --- | --- |
| Navigation/layout | Open home/shop, expand mobile nav; inspect gradients/cards/image sizing and overflow after CSS relocation | Passed at both widths; original styling retained, no body style tags |
| Blog create/edit/delete | Login as author, create a story, edit text without a new image, submit invalid image, recover, confirm then delete | Passed; validation recovers without a server error |
| Blog authorisation | Anonymous access; another member's direct form GET/POST; staff edit-form access | Login redirect / 403 / authorised staff form respectively |
| My pets | Add name/species/focus/notes; view reminder; edit focus; GET delete confirmation; POST delete | Passed; displayed data/reminder changes and profile deletes only after POST |
| Pet validation/privacy | Native 500-character limit; deliberately submit 501 characters; correct the form; try another owner and staff GET/POST | Error displayed and recovery passed; private records return 404 |
| Order history/reorder | Compare two accounts, attempt foreign reorder and GET mutation, reorder own fixture | Own records only; 404/405; current £7.25×2=£14.50 while historical £12.00 stays unchanged |
| Checkout without keys | Add a product through CSRF form, enter valid delivery data, submit | Clear unavailable-payment message; cart preserved; no Stripe Session created |
| Account recovery/navigation | Invalid reset link; switch login/signup with internal destination | Recovery explanation/new-link action and retained destination passed |

The order-history rows/screenshots use **manually seeded synthetic PAID fixtures**. They prove display/privacy/reordering, **not Stripe confirmation or a real transaction**. No actual private customer data is used.

Selected genuine local captures:

- [Mobile pet profile](evidence/28oct-mobile-pet-profile.png) and [server validation](evidence/28oct-mobile-pet-notes-validation.png)
- [Desktop blog edit](evidence/28oct-desktop-blog-edited.png)
- [Mobile checkout with absent keys](evidence/28oct-mobile-checkout-unconfigured.png)
- [Invalid reset recovery](evidence/28oct-desktop-invalid-reset.png)
- [Desktop homepage](evidence/28oct-desktop-home.png) and [mobile shop](evidence/28oct-mobile-shop.png)
- [Order-history fixture, not payment evidence](evidence/28oct-desktop-own-orders-synthetic.png)

## Genuine validator results

Nu Html Checker **26.10.12 (973e40b)** ran locally, not through an external validation website:

- **19 HTML documents, zero errors/warnings**: 17 actual rendered application pages, the new Facebook proposal and retrospective wireframes. Includes authenticated forms and deliberately invalid pet-form/reset states. [Report](evidence/28oct-nu-html-validation.json), [raw checker output](evidence/28oct-nu-html-raw.json).
- **2 project CSS files, zero messages**: `static/css/site.css`, `static/css/style.css`. Vendored Bootstrap is excluded from this project-authored CSS claim. [Report](evidence/28oct-nu-css-validation.json), [raw output](evidence/28oct-nu-css-raw.json).

An initial Nu run found body style blocks and skipped heading levels; those were fixed and a regression test was added. Browser reruns confirmed the moved/scoped CSS kept home/shop appearance.

An earlier `html-validate 10.3.0` recommended-style audit failed on inline style attributes and whitespace left by template rendering. Its rules were not disabled and this **is not claimed as passing**: [style-audit outcome](evidence/28oct-html-style-audit.json). It is separate from HTML/CSS conformance; the independent Nu rerun passed. No Lighthouse, full WCAG, other-browser or deployed-validator pass is claimed.

To reproduce conformance validation, install Node/npm and Java, capture **rendered** pages from a running local fixture site, keep raw HTML/CSRF values outside Git, then run:

```bash
npx --yes --package vnu-jar@26.10.12 vnu --format json /path/to/rendered/*.html docs/marketing/facebook-mockup.html docs/design/wireframes.html
npx --yes --package vnu-jar@26.10.12 vnu --format json --css static/css/site.css static/css/style.css
```

Django source templates must not be submitted as if their tags were rendered HTML. These optional validation tools are not application runtime dependencies.

## Build and deployment-readiness checks

`bash build.sh` was rerun locally with the project virtualenv, SQLite and development settings. Dependency installation, manifest/static collection and migrations including `accounts.0001` and `orders.0005` succeeded. Production-style `check --deploy --fail-level WARNING` passed with a newly generated ephemeral strong secret and configured Render host; the default development fallback secret correctly fails deployment checking.

Local Gunicorn/WhiteNoise smoke checks passed for public routes, private pet login redirect, collected static assets/crawler copies, correct sitemap host, HTTPS redirect/HSTS, and refusal of an unconfigured webhook: [results](evidence/28oct-production-smoke.json). The test uses a trusted-proxy HTTPS header and SQLite. It does **not** verify actual Render/PostgreSQL, external TLS, persistent storage or external services.

CI now has SQLite checks/build settings and a disposable PostgreSQL 16 job. PostgreSQL uses the explicit test-only `TEST_DATABASE_URL` and `petwell.postgres_test_settings`, never production `DATABASE_URL`. The threaded overlapping-worker test is enabled only there. Check the latest PR head's actual job status; do not infer its result from local SQLite. No private credentials or new production services are configured by CI.

## Remaining external/deployed acceptance — not yet passed here

The cloud runtime has no Stripe, Cloudinary, SMTP, production database or strong deployment-secret bindings. Read-only access to the Render host and direct GitHub API returned network-proxy denial; this is not a diagnosis that the deployed app is down. Native Git and public GitHub HTML remain reachable. A saved API-domain draft does not itself update the runtime policy.

| Check | Expected result | Current status |
| --- | --- | --- |
| Render configuration/migrations | Strong secret, DEBUG off, correct URL/hosts, persistent PostgreSQL, backups, all migrations, actual deploy checks | Owner configuration and approved deployment review required |
| Actual Stripe sandbox payment | Genuine hosted test checkout, matching signed endpoint event, pending→paid, correct cart reconciliation | Not run; credentials and approved deployment absent |
| Real decline/cancellation/duplicate/retry | Correct unpaid/cart handling and one confirmed order | Offline logic tested; actual sandbox delivery pending |
| Cloudinary | Correct authorised images, real upload/replace/clear and outage recovery | Offline adapter/fallbacks tested; external upload pending |
| SMTP/reset delivery | Verified sender and actual received reset email | Local email/token flow tested; real delivery pending |
| Product photos | Correct catalogue item, authorised image/source record | Owner-supplied genuine photos/rights still missing |
| Deployed browser/accessibility | Repeat matrix on actual released site; keyboard/contrast/zoom and other browsers | Local Chromium/markup checks completed; deployed/cross-browser checks pending |
| Marketing/design | Clearly labelled mockup or genuine page evidence, accurate original/retrospective design provenance | New mockup and retrospective diagrams rendered locally; no live campaign/page claimed |

See [ASSESSMENT_REVIEW.md](ASSESSMENT_REVIEW.md), [PR8_REVIEW.md](PR8_REVIEW.md) and [EVIDENCE.md](EVIDENCE.md). Do not mark pending integrations or original planning evidence as passed.
