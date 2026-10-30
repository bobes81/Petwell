# Test record — updated 30 October 2026, with earlier evidence retained

This record covers integrated PR #9 availability and supplied-image preflight in `fix/pp5-resubmission`, including safe image mapping and Gmail configuration after `d0bd4b2`, the earlier follow-up after `a6cd86a`, the local restored-copy profile, aged checkout-retry fix, earlier deployment/configuration fixes and the pet-profile feature. It is not a production or external-service test report. Meaningful regressions were added without disabling a failing assertion to obtain a pass.

## Later 30 October: image diagnosis and owner sandbox success

The owner verified public shop/cart function and one genuine GBP 11.49 sandbox Checkout with a complete/paid Session and paid production order on deployed `f75dbe1`. No customer/order/Session identifiers are published; the reviewer initiated no new payment. Auto-deploy is owner-confirmed disabled. The initial maintenance-enabled snapshot below is historical, not a new current-setting inspection. [Exact scope](evidence/30oct-production-deployment.md#later-owner-verified-acceptance-and-current-image-issue).

The owner also confirms ten non-empty image references but fallback images in the live shop. The provided persisted reference shape already generates the correct versioned HTTPS URL from a configured CloudinaryResource. The filter did fail for a plain string: it always returned the placeholder. It now parses the persisted shape through CloudinaryField, preserves the version/format/folders, enforces HTTPS on resources and retains safe fallback without changing stored data. This is a confirmed narrow helper fix, **not proof of the live production root cause**. [Actual baseline/fixed comparison](evidence/30oct-image-url-baseline-comparison.json).

**New actual local checks:** [44 focused tests passed](evidence/30oct-image-focused-tests.txt); [complete SQLite suite: 205 tests, 204 passed, one PostgreSQL-only skip, zero failures](evidence/30oct-image-full-sqlite-tests.txt). Fifteen regressions cover raw/resource/template/initial-src rendering, HTTPS/options, missing cloud, malformed/unsafe input and read-only diagnosis, including zero writes/uploads/fetches and no credential/signed-URL disclosure. Existing checkout, blog/auth/profile/history/migration coverage remains intact. No Stripe logic, database model/migration, product record or asset was changed.

[System/migration/production-style checks passed](evidence/30oct-image-readiness-checks.txt), with a new process-only secret and no provider/database credentials. No model changes are missing migrations. The new command requires the reviewed new code, defaults to no raw URLs and never fetches remote assets. [Precise owner diagnosis](PRODUCT_IMAGE_DIAGNOSIS.md). Public Render access here was proxy-blocked; no actual Cloudinary asset response, missing asset, live browser screenshot or external upload/SMTP pass is claimed. Final-head SQLite/PostgreSQL CI must be checked after push; the deployed 190-test record below retains its original scope.

Payment review reconfirmed pending-before-signature behavior, exact Session/reference/GBP/mode matching, immutable payload/idempotency/23-hour hold, lease recovery, preservation of old Session mappings and one-time cart reconciliation. Existing regressions already cover these cases; no duplicate amount-only payment test or extra transaction was added.

## 30 October production deployment and real-backup rehearsal

The owner verified deployment of **`f75dbe1c6fb9c16f3895a5b01451e2de4d9b9160`**, successful build and all six project migrations. Render is running the revision with **Maintenance Mode still enabled**. These are owner-verified production facts; the reviewer did not access the private dashboard or production database. They do not establish public/browser/provider acceptance.

The reviewer separately completed the actual uploaded-backup rehearsal on disposable PostgreSQL 18.6: all six migrations applied, all original rows/fields in 22 tables preserved, 10 products / 5 orders / 5 items / 2 posts / 2 subscribers retained, zero missing item links, five unique legacy UUIDs with unpaid defaults, no pending migrations and passing local system check. Only expected new Django metadata was added. [Sanitised actual result](evidence/30oct-real-backup-migration-rehearsal.json), [complete source/scope record](evidence/30oct-production-deployment.md). The code/migrations rehearsed at `1ad2b4c` are identical to deployed `f75dbe1`; later changes were documentation only. No repeat rehearsal or local full-suite run was performed for this update.

The deployed baseline's [CI](https://github.com/bobes81/Petwell/actions/runs/41010383682) passed: SQLite **189 passed / one PostgreSQL-only skip**, PostgreSQL **190 passed** (16/18 CI matrix; saved local 18.6 output below). Stripe, SMTP, Cloudinary and live browser testing remain **unverified**, not failed or retrospectively passed. Existing screenshots and Nu results retain their local scope. Production counts/secret settings/cutover details are not inferred from the backup rehearsal. [Remaining owner checks](OWNER_RELEASE_CHECKLIST.md).

## Earlier 30 October documentation audit

The [morning handoff](MORNING_HANDOFF.md) records a fresh source/documentation review and static link/evidence checks. No application code or migration changed, so no local Django tests were rerun. The latest 190-test results below are the actual 29 October application-baseline runs; they are not claimed as new executions today. The stale latest-test/validator entries in EVIDENCE.md now match those existing artifacts.

## Automated checks actually run

```bash
python manage.py test --settings=petwell.test_settings --verbosity=2
python manage.py check --settings=petwell.test_settings
python manage.py makemigrations --check --dry-run --settings=petwell.test_settings
python -m pip check
```

**Latest PR-branch SQLite result: 205 discovered/executed tests — 204 passed, 1 explicitly skipped, 0 failures.** The deployed `f75dbe1` baseline remains 190 tests (189 passed/one skip). The skip is the PostgreSQL-only two-worker concurrency test. Deterministic stale-session, busy-lease, lease recovery/takeover, immutable-payload and payment-state tests run locally. Do not describe the SQLite run as proof of simultaneous PostgreSQL workers.

The test database is isolated and email is in memory. Stripe create/retrieve/expire and Cloudinary uploads are mocked; actual HMAC verification runs against signed fixture payloads. No test processes a payment, uploads an external image or delivers an email. [Latest actual SQLite output](evidence/30oct-image-full-sqlite-tests.txt). Earlier [116-test run](evidence/28oct-confirmed-history-tests.txt), [114-test migration](evidence/28oct-deployment-readiness-tests.txt), [Cloudinary compatibility](evidence/28oct-render-compatibility-tests.txt) and [108-test original](evidence/django-tests.txt) outputs remain preserved.

System checks, migration consistency and installed dependency checks passed. Selected Python error/import lint and whitespace checks passed. The repository changes were reviewed for English content, common real credential patterns, private-correspondence copying and broken relative documentation links; no matching accidental credentials/private text were found. Test passwords and the disposable CI PostgreSQL password are explicitly synthetic fixtures, not deployment credentials.

## 30 October release handoff and guarded PDF procedure

After `98754a3`, the safe withdrawal command and **11 synthetic regressions** were added. The complete suites actually ran: **SQLite 190 tests, 189 passed, one PostgreSQL-only skip, zero failures** ([raw output](evidence/29oct-release-handoff-sqlite.txt)); **local PostgreSQL 18.6: 190 passed, zero skips/failures** ([raw output](evidence/29oct-release-handoff-postgresql18.txt)). This includes the existing migration/concurrent-checkout tests; no production or owner-restored database was accessed. The disposable Docker service used loopback port 55438, synthetic credentials and no existing-data mounts; its test database and container were removed afterward.

The command tests cover read-only exact-name discovery without sensitive history, duplicate candidates without automatic selection, all mandatory approval guards, wrong IDs/names/stale snapshots, version-only image changes, genuine SQL NULL versus empty image references, preserved fields/order/item history, active lease refusal, conditional conflict rollback and repeat application with no UPDATE. Provider sockets/uploads are refused in these tests. They do not identify the actual PDF, prove a checkout pause or reconcile provider obligations.

The first additional NULL/empty-image regression failed because its fixture used CloudinaryField's normal conversion: an empty Python string was saved as SQL NULL. [The initial full-run failure is retained](evidence/29oct-release-handoff-initial-fixture-failure.txt). The fixture now uses typed SQL expressions to create the two genuinely different stored states; the command was not weakened and the stale-snapshot assertion remains. Both final complete suites above pass.

[System/migration/link/content checks](evidence/29oct-release-handoff-checks.txt) passed: no system issues or missing migrations; 312 relative README/documentation links, including local anchors, resolve. Changed text was checked for English content, common real credential patterns and private-feedback copying, and whitespace checks passed. This is not a general security certification or external URL uptime check. Earlier provider/configuration/static/browser runs below retain their original scope; no unchanged browser screenshots were unnecessarily recreated for this CLI/documentation change. The final pushed SHA's GitHub checks must be verified separately; previous green CI is not a new-head result.

The [exact-record withdrawal procedure](LEGACY_PDF_WITHDRAWAL.md), [nontechnical release/recovery plan](RELEASE_2026-10-30.md), [device guide](IPAD_MACBOOK_CHECKLIST.md) and [Pass matrix](PASS_COMPLIANCE_MATRIX.md) document conditional owner approval, remaining production/provider gates and unknown service capabilities. This review did not deploy, change accounts or execute the production procedure.

## Final independent pre-deployment review

Starting from `ecf0b92`, independent assessment, asset and payment/auth reviews found no additional required feature gap in the supplied feedback. The full official guide remains unavailable. Story IDs/statuses were corrected, and one confirmed presentation defect was fixed: cover fitting cropped square concept artwork/footer on mobile. A scoped AI-only contain fit preserves the whole source; ordinary images retain their styling. The new regression verifies that scope. [33 focused asset/configuration tests passed](evidence/29oct-final-asset-tests.txt); [97 payment/auth tests: 96 passed, one PostgreSQL-only skip](evidence/29oct-final-payment-auth-audit.txt).

**Final complete suite:** SQLite **179 tests, 178 passed, one PostgreSQL-only skip, zero failures** ([raw output](evidence/29oct-final-sqlite-tests.txt)); local Docker PostgreSQL **18.6: 179 passed, zero skips/failures** ([raw output](evidence/29oct-final-postgresql18-tests.txt)). The overlapping-worker test actually ran on PostgreSQL. This is real database/ORM testing with synthetic fixtures, not Stripe/Cloudinary/SMTP acceptance.

**Local PostgreSQL migration rehearsal:** an isolated loopback-only Docker service with no existing-data mounts ran both historical/incremental migration regressions: **two passed, zero failures/skips** ([raw output](evidence/29oct-final-postgresql18-migrations.txt), [observed environment/scope/cleanup](evidence/29oct-final-postgresql-rehearsal.json)). The incremental case starts after the five owner-rehearsed migrations, requires only products.0002 and preserves two synthetic products (including PDF), one pending order/item and field/link state without automatic withdrawal; the other case preserves the full synthetic original commerce/blog/subscriber history. No owner backup, Mac or production data was accessed. The test database and temporary container were removed.

Reproduction uses an already available local Docker daemon and a new disposable container, not a paid database or an existing valuable database:

```bash
docker run --name petwell-review-pg --rm -d -p 127.0.0.1:55438:5432 -e POSTGRES_DB=petwell_review -e POSTGRES_USER=petwell_review -e POSTGRES_PASSWORD=synthetic_local_rehearsal_only postgres:18
# Wait for this exact disposable service to report ready before tests.
docker exec petwell-review-pg pg_isready -U petwell_review -d petwell_review
export TEST_DATABASE_URL=postgres://petwell_review:synthetic_local_rehearsal_only@127.0.0.1:55438/petwell_review
python manage.py test orders.tests.AvailabilityMigrationTests orders.tests.ExistingOrdersMigrationTests --settings=petwell.postgres_test_settings --verbosity=2
python manage.py test --settings=petwell.postgres_test_settings --verbosity=2
docker stop petwell-review-pg
unset TEST_DATABASE_URL
```

The password above is an explicit disposable fixture, not a deployment credential. Never substitute a production/valuable restored URL. The recorded image digest/version identifies the actual run; a later floating tag can differ. This older synthetic rehearsal did not establish real-data compatibility or Render downtime. The later actual uploaded-backup rehearsal and owner-verified production migration success, recorded above, complete the migration gates; do not repeat the previously pending targeted check.

**Final running-app Chromium review:** [actual report](evidence/29oct-final-browser-results.json), 1440×1000 and 390×844, **12 grouped checks and 16 genuine screenshots**. It exercises actual local signup/login/logout and reset-request UX, auth destinations/invalid-reset recovery, navigation, unavailable-payment form behavior, blog CRUD/image validation/direct permissions, owner-only pet CRUD/validation/reminders and order privacy/current-price reorder. Forms have labels, captured main pages have one H1, images have alt attributes and no document overflow/broken images/JS exceptions/external page requests were detected. Email is dummy, provider calls are refused and paid orders are manually seeded fixtures; no delivery/payment/customer/deployed evidence is implied. The local server was stopped. These basic checks are not full WCAG, contrast, zoom or other-browser certification.

**Concept CSS preview:** [measured before/after report](evidence/29oct-concept-css-preview.json), [desktop](evidence/29oct-concept-css-preview-desktop.png), [mobile](evidence/29oct-concept-css-preview-mobile.png). All nine unchanged originals were rendered in data URLs with project CSS at 390/430/768/1440 widths. The measured crop disappears after contain fitting. This is an explicitly labelled isolated CSS preview, not a Django product assignment, Cloudinary asset or deployed shop. No source bytes/operational IDs/rights flags were changed.

**Final validation:** local Nu Html Checker 26.10.12 (973e40b): **22 HTML documents** (20 actual rendered fixture pages plus two labelled design artifacts), **two project CSS files**, **zero messages**. [Summary](evidence/29oct-final-validation-summary.json), [raw HTML result](evidence/29oct-final-nu-html.json), [raw CSS result](evidence/29oct-final-nu-css.json). Raw HTML/tokens remain outside Git. This is not a new external validator or full-accessibility pass. [Final system/migration/deployment/static/dependency checks](evidence/29oct-final-readiness-checks.txt) passed sequentially with synthetic/process-only configuration; the pip cache ownership warning was non-blocking.

This earlier cutover-review status is superseded by the completed deployment/build/six migrations recorded above. Maintenance remains enabled; catalogue decisions and genuine provider/live-browser acceptance remain outstanding before opening checkout or claiming full submission readiness. Follow [the short ordered owner checklist](OWNER_RELEASE_CHECKLIST.md). Earlier records below retain their original counts, dates and scope; verify the final submitted head's CI rather than attributing older results to it.

## Earlier integrated PR #9 and supplied concept sources

The fetched PR #9 `b39ec91` passed 164 SQLite tests (163 passed/one skip). The reviewed `e1dcc1e` passed 172 (171 passed/one skip), with successful SQLite/PostgreSQL 16/18 CI: [PR #9 run](https://github.com/bobes81/Petwell/actions/runs/40897334783). [Detailed review and raw outputs](PR9_REVIEW_AND_RELEASE_GATES.md). PR #9 history is incorporated into the main feature branch; production main remains unchanged.

The integrated suite passed **178 tests: 177 passed, 1 PostgreSQL-only skip, 0 failures**. [Raw output](evidence/29oct-integrated-resubmission-tests.txt). New coverage verifies unavailable/missing/zero/negative checkout rejection for guests and members before order/lease/API creation, stale mixed-cart recovery, honest all-unavailable/mixed reorder feedback, seed preservation, the one-field migration from the owner-rehearsed schema and valid signed confirmation for an already-issued Session after withdrawal. The latter records payment evidence without creating a transaction or assuming withdrawal expires a hosted URL.

Six image-source regressions cover incomplete source-only validation with zero SQL/provider calls, refusal of source-only application, unchanged strict default validation, damaged/mismatched sources and the actual committed draft/PNGs. [20 focused mapping/source tests](evidence/29oct-source-preflight-tests.txt) passed before integration; the complete suite additionally checks the real bundle and preservation of withdrawal flags. [Actual owner-file preflight](evidence/29oct-uploaded-concepts-preflight.txt) accepted all nine unchanged 1000×1000 PNGs/hashes with all operational identifiers unset and rights pending. Normal dry-run/application and incompatible flags were deliberately refused. No Cloudinary ID, version or product primary key was invented.

A new [local Chromium check](evidence/29oct-availability-browser.json) passed eight grouped checks at 1440×1000 and 390×844, with four genuine screenshots: [mobile stale cart](evidence/29oct-availability-mobile-stale-cart.png), [desktop stale cart](evidence/29oct-availability-desktop-stale-cart.png), [mobile withdrawn reorder](evidence/29oct-availability-mobile-withdrawn-reorder.png), [desktop withdrawn reorder](evidence/29oct-availability-desktop-withdrawn-reorder.png). It uses a separate temporary SQLite database, synthetic catalogue, seeded sessions and manually seeded PAID history fixtures, not a provider payment. Shop visibility, stale-cart POST400/removal recovery, current-price reorder and truthful skipped/no-add feedback passed. Initial visual inspection found broken price/header wrapping; scoped horizontal table scrolling now preserves single-line amounts, focusable labelled scroll access and body width. Final checks detected no document overflow, broken image, JS error, external page request or server provider attempt. No full accessibility/cross-browser or deployed pass is claimed.

[Final system/migration/deployment/static/dependency checks](evidence/29oct-integrated-readiness-checks.txt) passed sequentially after the test suite and after stopping the local browser server. No model changes were missing migrations; production-style checks used synthetic credentials and an ephemeral key, not actual services. The pip cache-ownership warning was non-blocking.

The availability migration is new relative to the owner's completed five-migration real-data rehearsal. Synthetic initial-to-six and incremental-products.0002 fixtures preserve fields/links/default availability; old Product writers demonstrably fail after the new required field. At that earlier point this later migration needed a targeted real-data check. The 30 October six-migration rehearsal and owner-verified production application now complete that check; actual PDF withdrawal is still unverified. The owner-provided concept files are repository review assets, not uploaded catalogue imagery or product photographs. Earlier results below retain their dates/counts and scope.

## Earlier 29 October: image-association safety and Gmail configuration before ZIP receipt

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
| Migrations | Upgrade from confirmed order/product initial plus complete blog history/dependencies; six pending project migrations from the original baseline, including new products.0002; no replay of applied blog/product initial history; preserved member/guest orders/items, product/article images, story and subscriber fields; unique pending UUIDs; usable new tables/protected references; old-worker cutover constraint; consistent completed history |

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
| Product images | Accurate item matching, authorised and honestly labelled image/source record | Nine actual source concepts inspected with matching hashes/names; owner rights/accuracy approval and actual upload/association pending |
| Deployed browser/accessibility | Repeat matrix on actual released site; keyboard/contrast/zoom and other browsers | Local Chromium/markup checks completed; deployed/cross-browser checks pending |
| Marketing/design | Clearly labelled mockup or genuine page evidence, accurate original/retrospective design provenance | New mockup and retrospective diagrams rendered locally; no live campaign/page claimed |

See [ASSESSMENT_REVIEW.md](ASSESSMENT_REVIEW.md), [PR8_REVIEW.md](PR8_REVIEW.md) and [EVIDENCE.md](EVIDENCE.md). Do not mark pending integrations or original planning evidence as passed.
