# Test record — 29 October 2026, with earlier evidence retained

This record covers `fix/pp5-resubmission`, including safe image mapping and Gmail configuration after `d0bd4b2`, the earlier follow-up after `a6cd86a`, the local restored-copy profile, aged checkout-retry fix, earlier deployment/configuration fixes and the pet-profile feature. It is not a production or external-service test report. Meaningful regressions were added without disabling a failing assertion to obtain a pass.

## Automated checks actually run

```bash
python manage.py test --settings=petwell.test_settings --verbosity=2
python manage.py check --settings=petwell.test_settings
python manage.py makemigrations --check --dry-run --settings=petwell.test_settings
python -m pip check
```

**Latest SQLite result: 155 discovered/executed tests — 154 passed, 1 explicitly skipped, 0 failures.** The skip is the PostgreSQL-only two-worker concurrency test. Deterministic stale-session, busy-lease, lease recovery/takeover, immutable-payload and payment-state tests run locally. Do not describe the SQLite run as proof of simultaneous PostgreSQL workers.

The test database is isolated and email is in memory. Stripe create/retrieve/expire and Cloudinary uploads are mocked; actual HMAC verification runs against signed fixture payloads. No test processes a payment, uploads an external image or delivers an email. [Latest actual local output](evidence/29oct-catalogue-gmail-tests.txt). Earlier [116-test run](evidence/28oct-confirmed-history-tests.txt), [114-test migration](evidence/28oct-deployment-readiness-tests.txt), [Cloudinary compatibility](evidence/28oct-render-compatibility-tests.txt) and [108-test original](evidence/django-tests.txt) outputs remain preserved.

System checks, migration consistency and installed dependency checks passed. Selected Python error/import lint and whitespace checks passed. The repository changes were reviewed for English content, common real credential patterns, private-correspondence copying and broken relative documentation links; no matching accidental credentials/private text were found. Test passwords and the disposable CI PostgreSQL password are explicitly synthetic fixtures, not deployment credentials.

## 29 October: image-association safety and Gmail configuration

The new full SQLite run discovered **155 tests: 154 passed, 1 PostgreSQL-only skip, 0 failures**. Twenty regressions were added after `d0bd4b2`, without changing the database schema or disabling assertions.

- [15 focused image-association tests passed](evidence/29oct-image-association-tests.txt): default dry-run has no database writes, uploads or fetches; explicit application fills only empty references (both SQL NULL and genuine SQL empty strings); existing images, catalogue fields, PDF and order history are preserved; re-running is non-destructive and conflicts roll back earlier assignments. Additional checks cover real temporary PNG/JPEG/WEBP files, SHA/size/format validation, corrupted PNG CRC, decompression warnings, source path escapes/symlinks, invalid/duplicate/deep JSON, non-regular manifest files (including FIFO), cloud/record identity and the AI-illustration caption. Files are tiny synthetic test fixtures, not the owner's nine assets or proof of actual AI generation.
- [17 focused Gmail/configuration/rehearsal tests passed](evidence/29oct-gmail-configuration-tests.txt), including five new SMTP regressions. These verify Gmail STARTTLS settings, provider-secret isolation, explicit password precedence/disable, SSL selection and sanitized invalid-option errors. The rehearsal still disables inherited Gmail credentials. Probe sockets are refused; no SMTP authentication or email delivery occurred.
- [System/migration/production-settings/static/dependency checks passed](evidence/29oct-catalogue-gmail-checks.txt) with process-only synthetic Gmail/Cloudinary credentials and a fresh ephemeral Django secret. No migrations were generated. The blank manifest's actual CLI invocation deliberately returned exit 1 before association; it is a safety refusal, not a successful asset import. The pip cache-ownership warning did not affect dependency consistency.

The first combined 154-test run had **one error and one skip** because the reviewer ran `collectstatic` concurrently with tests sharing that directory. WhiteNoise encountered a file being replaced: [unaltered failed output](evidence/29oct-catalogue-gmail-initial-race.txt). The checks were separated and the final 155-test suite passed sequentially after the manifest safety regression was added. No assertion was removed or static-file error hidden; CI already runs tests and collection sequentially within each isolated job.

[The image/PDF workflow](CATALOGUE_IMAGES.md) contains only a blank prospective manifest; no owner originals, source rights, real asset uploads or production assignments were verified. The PDF proposal preserves history and requires verified fulfilment or complete withdrawal before checkout is enabled. Public Render/Google help-page retrieval was proxy-blocked on 29 October; this is neither an SMTP connectivity test nor a diagnosis that those services are down. References: [Render free-service documentation](https://render.com/docs/free), [Google App Password help](https://support.google.com/accounts/answer/185833?hl=en). Existing-account App Password eligibility and actual Render SMTP egress/delivery remain owner checks. Stripe acceptance retains the genuine sandbox/site-created Session and signed matching-webhook requirements in [the Render matrix](RENDER_CHECKLIST.md).

No external image, email, payment or deployment acceptance was performed, and no new screenshot/validator run is claimed for this follow-up. Earlier evidence keeps its original scope.

## 29 October follow-up after the successful owner rehearsal

Ten meaningful regressions and three small behavior changes follow `a6cd86a`; no model or migration changed. The then-current **135-test** SQLite suite passed: [earlier complete output](evidence/29oct-pass-readiness-tests.txt). [Actual system/migration/deployment/static/dependency checks](evidence/29oct-pass-readiness-checks.txt) also passed using synthetic/process-only configuration. The `pip check` cache-ownership warning is non-blocking; dependency consistency passed.

- **PostgreSQL checkout error prevention:** a valid 255-character email passed the old default form limit but exceeded `Order.email`'s 254-character database column. The new boundary test failed before the fix: [actual 2-test output, 1 failed / 1 passed](evidence/29oct-email-boundary-before.txt). The form now rejects it before creating an order/lease or calling Stripe, preserves the cart, and accepts 254 characters. PostgreSQL CI exercises the same boundary; SQLite alone does not enforce `varchar` length.
- **Signed webhook race:** a cookieless CSRF-enforcing sender delivers a genuine HMAC-signed fixture while mocked Session creation has not yet persisted its ID. The endpoint returns 503, stays pending, then accepts the same event after the mapping is saved. Re-delivery keeps one paid order and the original timestamp; only the customer's later request clears the cart.
- **Rate-limit recovery:** a mocked provider 429 keeps the cart/order/frozen payload, releases the lease, hides provider diagnostics and retries using the same idempotency key/payload. A signed fixture, rather than the browser return, confirms payment. Together with the email boundary and staff privacy check, [five focused commerce regressions passed](evidence/29oct-pass-readiness-checkout.txt).
- **Order privacy:** staff status does not grant storefront access to another customer's history, confirmation or reorder. Administrative permissions remain a separate interface.
- **Account recovery:** generic reset completion does not reveal account existence or promise email delivery. Tests verify HTTPS Render-host links behind the trusted proxy and invalidate another authenticated browser after a successful reset. Messages stay in Django's in-memory outbox; no SMTP delivery is claimed.
- **Catalogue fulfilment:** fresh development seeding omits the unsupported PDF download. Re-seeding preserves existing product data, images, prices and the legacy PDF rather than deleting production/customer history. Existing offered PDFs still require owner action. [Accounts/products/configuration focused run: 32 passed](evidence/29oct-pass-readiness-accounts-products.txt).

No external Stripe, Cloudinary, SMTP or Render acceptance was performed. The new offline tests supplement the earlier failure/expiry/retry/signature/image/permissions coverage; they do not replace provider acceptance. Existing screenshots retain their original dates and scope, and no new screenshot or external-validator result is claimed for this follow-up.

## 29 October: restored-copy configuration and old ambiguous checkout attempts

The owner subsequently completed the full isolated Mac PostgreSQL 18 working-copy rehearsal on 29 October: all five pending migrations applied with none remaining; original 10 products, 5 orders, 5 order items, 2 posts and 2 subscribers preserved; zero missing/duplicate order UUIDs, missing order links or incorrectly paid legacy orders. Local shop/cart/unavailable-payment protection, signup/login/logout, private pet CRUD, blog CRUD and a new user's empty history passed. These are **owner-reported manual results**: [dated record](evidence/29oct-owner-rehearsal.md). This review did not access the database or receive raw outputs/screenshots. The [procedure](RESTORED_DB_REHEARSAL.md) remains a reproduction reference; the completed working-copy checks need not be repeated. Production cutover and external acceptance remain separate.

Six startup tests verify `petwell.rehearsal_settings`: explicit local PostgreSQL URL with no production fallback; local SSL not forced; remote/maintenance/routing-override targets rejected; separate local secret required; Stripe/Cloudinary/SMTP disabled despite valid inherited service fixtures; IPv6 loopback accepted. Probe sockets are blocked and no database is connected: [actual focused output](evidence/29oct-rehearsal-settings.txt). Ordinary production settings retain required database SSL. A loopback guard cannot prove a port is not forwarded; the owner must verify the local working-copy target. Clear stale production bindings as documented because base settings still parse them before overrides.

Three checkout regressions found a real recovery defect: after a create response was lost, the frozen request could be retried indefinitely without a saved Session ID, even after Stripe may prune its idempotency key. The focused pre-fix run had **3 tests, 2 failures**: [before](evidence/29oct-aged-retry-before.txt). The fix holds automatic unmapped retries at 23 hours from order creation, preserving the order/payload/cart and active pointer for approved reconciliation. Changed cart/contact data cannot bypass it, and a known 25-hour-old Session is still retrieved without marking paid from its return. All three now pass: [after](evidence/29oct-aged-retry-after.txt). The [Stripe idempotency API reference](https://docs.stripe.com/api/idempotent_requests) is a design reference; this runtime's public-documentation request was proxy-blocked, and no payment API acceptance was performed.

CI now includes PostgreSQL 16 and 18, retaining the original `postgres` check name for 16 and adding `postgres-18`. Each job also connects the local rehearsal profile to its synthetic service for `check`/`migrate --plan`, with transaction read-only mode enabled; this exercises connection/configuration without migrating the owner's restore. Verify the exact submitted head's job results. Neither CI nor the startup probes prove the owner's Mac rehearsal passed. Previous browser/validator images retain their original dates/scope. System/migration/deployment/dependency checks were rerun locally with synthetic/process-only configuration: [actual output](evidence/29oct-system-checks.txt).

A targeted 29 October Chromium check rendered the new aged-attempt hold at 1440×1000 and 390×844: [desktop](evidence/29oct-aged-retry-desktop.png), [mobile](evidence/29oct-aged-retry-mobile.png), [actual report](evidence/29oct-aged-retry-browser-results.json). Both returned HTTP 200, showed the review/cart-preservation messages, retained pending order/payload/cart/pointer and released the lease. No overflow, broken image, JavaScript exception or external request was detected in those two states. This used a new synthetic SQLite fixture, fake keys and refused Stripe/outbound server connections (zero API attempts); it did not use the owner's restored data or verify payment processing. The temporary server was stopped after capture. This narrow check is separate from the earlier broader browser matrix below.

A further offline review resumed from `1f95d4b` on 28 October and changed documentation only. The full suite was rerun with the same result: **108 tests, 107 passed, 1 PostgreSQL-only skip, 0 failures**. System checks, migration consistency, production-style `check --deploy` (ephemeral local secret, no external services) and `pip check` passed again. [Follow-up test output](evidence/28oct-followup-django-tests.txt) and [review/CI record](evidence/28oct-followup-review.json) preserve this verification separately. Existing browser/validator screenshots and reports were reviewed, not recaptured or represented as new runs.

## Cloudinary URL and Render configuration regression

The owner subsequently reported the existing Render variable names `CLOUDINARY_URL`, `DATABASE_URL`, `DEBUG` and `SECRET_KEY`. Their values were not inspected. Settings previously overwrote the SDK's URL-loaded credentials with missing separate values, losing the cloud name/API credentials and producing an invalid empty-cloud media URL. The new fresh-process regressions first reported **6 tests, 3 failures** against that code: [before-fix output](evidence/28oct-cloudinary-regressions-before.txt).

The fix preserves SDK-loaded credentials, forces HTTPS and derives the storage dictionary/media URL from the same resolved configuration. Six new tests now pass: URL-only startup through storage-package import; separate-variable compatibility; SDK-native precedence when both sources exist; HTTPS despite a conflicting URL query; missing-service defaults; and explicit SendGrid/TLS configuration. Probes use synthetic credentials, strip inherited service settings, block socket connections and expose only public fields/credential-match booleans. The PostgreSQL URL fixture is parsed for engine/SSL settings without contacting a database. No real upload, payment or SMTP delivery is claimed.

System/migration/deployment checks, static collection and dependency consistency also passed with a synthetic Cloudinary URL and a process-only ephemeral Django secret: [check output](evidence/28oct-render-compatibility-checks.txt). No new migration is required; the isolated full suite applies fresh migrations and exercises the legacy-order migration. The confirmed production project-app baseline and successful owner-reported restored-copy upgrade are recorded below; this review did not inspect production for subsequent drift. See [Render checklist](RENDER_CHECKLIST.md) before any approved release.

## Deployment-readiness migration rehearsal

The owner now confirms applied `orders.0001_initial`, `products.0001_initial` and blog through `0004_merge_20260213_0814`, including both branches and the merge. All those files match `main` (`6f0ac78`). At that review point, `orders.0002`–`0005` and `accounts.0001` were confirmed pending in production; they have since passed the owner's isolated real-data rehearsal, not a production release. Other production installed-app history/schema was not inspected. The existing migration regression was updated to that baseline rather than duplicated. Two additional webhook regressions bring the suite to **116 tests, 115 passed, 1 PostgreSQL-only skip, 0 failures**.

The fixture reconstructs that baseline plus its required auth/contenttypes dependency closure, inserts synthetic member/guest orders/items, a product/image reference, an existing story/image and a subscriber, then upgrades the entire graph. It requires exactly the five pending project migrations and no product/blog replay. Assertions preserve primary/foreign keys, article/subscriber content, image references, contact fields, timestamps, quantities and historical prices, verify unique pending UUIDs/empty payment fields, exercise new tables/protected deletion and require consistent completed history. The old-model insert still fails after upgrade because required new fields use application defaults; this is a verified cutover constraint. [Updated focused output](evidence/28oct-confirmed-blog-migration-tests.txt); the [earlier partial-history rehearsal](evidence/28oct-deployment-migration-test.txt) retains its original scope.

Migration reset/reversal exists only to construct a disposable fixture; it is not a production rollback procedure. The regression runs in both configured CI backends. Local system/migration checks, production-style `check --deploy` and dependency checks passed using SQLite and synthetic/process-only configuration: [latest actual output](evidence/28oct-confirmed-history-checks.txt). No production database, customer data, private settings, webhook destination or Render service was accessed. The [release recommendation remains NO-GO](RENDER_CHECKLIST.md) pending the remaining gates. The [recovery runbook](RELEASE_RUNBOOK.md) explains partial migration failure and the separate need to preserve/reconcile post-backup writes and externally issued Stripe Sessions.

## Additional signed-webhook regressions

Two new offline tests exercise real HMAC verification against synthetic JSON deliveries: [focused output](evidence/28oct-sandbox-webhook-followup-tests.txt).

- A fresh client with CSRF enforcement and no cookies receives HTTP 400 for a wrong signature and HTTP 200 for a valid signature. No session cookie is created. The signed delivery marks only the order state; the customer's cart remains until the next browser cart visit reconciles it.
- An unpaid completion and async failure keep the order pending/cart intact; async success marks paid. Later distinct success event IDs and delayed failure/expiry/unpaid events preserve `paid_at`, the single order and a newly added cart line after the purchased line was cleared.

The deployment checklist requests the two documented successful checkout events; synthetic failure/expiry deliveries are defensive ignore-path tests, not claims that the live endpoint received those events. No actual Stripe Session was created or payment processed. No further application-code defect was found by this review.

| Area | Meaningful regression coverage |
| --- | --- |
| PetProfile | Complete owner-only CRUD; owner assigned server-side; no access by another member/staff; CSRF; supported species/focus; required/overlong validation; escaped text; focus reminder |
| Blog | Author/staff CRUD; anonymous login requirement; direct non-owner GET/POST denial; GET delete confirmation; retained/cleared/new/invalid/oversized image; upload failure and absent Cloudinary configuration |
| Accounts | Signup/login, strong password checks, internal `next` retained across auth links, external redirects rejected, invalid/expired/sessionless/used reset links, successful reset via local email fixture |
| Configuration | URL-only Cloudinary startup and storage consistency, HTTPS, separate-variable fallback/precedence, PostgreSQL SSL parsing, disabled unconfigured Stripe, console default, Gmail/SendGrid isolation, explicit SMTP/TLS/SSL options and sanitized invalid-setting errors; no external connections |
| Payment creation | Database prices, bounded cart quantities, required API/signing keys, test/live mismatch rejection, frozen retries after lost responses/product rename/cart reordering |
| Payment lifecycle | Open/complete/expired Session states, expiry races/failure, changed data cannot bypass completed checkout, no replacement before old payable Session is closed,23-hour hold for old unmapped retries, older mapped Session recovery, recoverable errors |
| Checkout coordination | Durable active-order pointer; preloaded stale worker requests deduplicated; busy lease refuses a second attempt; stale holder cannot overwrite/release a newer lease; interrupted holder releases safely |
| Signed webhooks | Valid signature and exact amount/currency/order/reference/mode; invalid/stale signature and malformed signed structures; cookieless CSRF-enforcing delivery; distinct success IDs and delayed failure/expiry/unpaid events; timestamp/cart preservation; late mapping retry; no return-URL payment confirmation |
| Cart/orders | Clear once only after confirmation; keep newly re-added lines/additional quantities; own history only; owner-only POST reorder at current prices; historical totals preserved; protected product/order deletion |
| SEO/markup | Render crawler URLs, public blog entries, private-page noindex and no canonical, trusted configured canonical host without query parameters, escaped metadata, public/form links and fallback images, complete heading outline and no body style blocks |
| Migrations | Upgrade from confirmed order/product initial plus complete blog history/dependencies; exactly five pending project migrations with no blog/product replay; preserved member/guest orders/items, product/article images, story and subscriber fields; unique pending UUIDs; usable new tables/protected references; old-worker cutover constraint; consistent completed history |

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

CI has SQLite checks/build settings and disposable PostgreSQL 16/18 jobs. They use the explicit test-only `TEST_DATABASE_URL` and `petwell.postgres_test_settings`, never production `DATABASE_URL`. The threaded overlapping-worker test is enabled there. Check the latest PR head's actual job status; do not infer its result from local SQLite. No private credentials or new production services are configured by CI.

## Remaining external/deployed acceptance — not yet passed here

The cloud runtime has no Stripe, Cloudinary, SMTP, production database or strong deployment-secret bindings. Read-only access to the Render host and direct GitHub API returned network-proxy denial; this is not a diagnosis that the deployed app is down. Native Git and public GitHub HTML remain reachable. A saved API-domain draft does not itself update the runtime policy.

| Check | Expected result | Current status |
| --- | --- | --- |
| Render configuration/migrations | Strong secret, DEBUG off, correct URL/hosts, persistent PostgreSQL, backups, all migrations, actual deploy checks | Owner configuration and approved deployment review required |
| Actual Stripe sandbox payment | Genuine hosted test checkout, matching signed endpoint event, pending→paid, correct cart reconciliation | Not run; credentials and approved deployment absent |
| Real decline/cancellation/duplicate/retry | Correct unpaid/cart handling and one confirmed order | Offline logic tested; actual sandbox delivery pending |
| Cloudinary | Correct authorised images, real upload/replace/clear and outage recovery | Offline adapter/fallbacks tested; external upload pending |
| SMTP/reset delivery | Verified sender and actual received reset email | Local email/token flow tested; real delivery pending |
| Product images | Accurate item matching, authorised and honestly labelled image/source record | Nine planned AI originals not supplied/verified; no actual upload/association claimed |
| Deployed browser/accessibility | Repeat matrix on actual released site; keyboard/contrast/zoom and other browsers | Local Chromium/markup checks completed; deployed/cross-browser checks pending |
| Marketing/design | Clearly labelled mockup or genuine page evidence, accurate original/retrospective design provenance | New mockup and retrospective diagrams rendered locally; no live campaign/page claimed |

See [ASSESSMENT_REVIEW.md](ASSESSMENT_REVIEW.md), [PR8_REVIEW.md](PR8_REVIEW.md) and [EVIDENCE.md](EVIDENCE.md). Do not mark pending integrations or original planning evidence as passed.
