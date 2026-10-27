# Test record and remaining acceptance checks

Date: **27 October 2026**, local isolated cloud development environment. This record is for the resubmission branch, not a production test report. Rerun against the final submitted commit. No production deployment, real card charge or external upload was performed.

## Automated Django tests

```bash
python manage.py test --settings=petwell.test_settings
python manage.py check --settings=petwell.test_settings
python manage.py makemigrations --check --dry-run --settings=petwell.test_settings
python -m pip check
```

**PR #8 review result: 63 tests passed; zero failed, skipped or expected failures.** The original 46 tests also passed before the review; added regressions exposed previously untested bugs before fixing them. Django system checks reported no issues and no missing migrations were detected. Installed dependency requirements are consistent. The test database is in-memory SQLite and emails are in memory. Stripe session creation and Cloudinary uploads are mocked; webhook signatures use real HMAC signing and Stripe's signature verifier with an offline fixture secret.

| Area | Automated coverage |
| --- | --- |
| Checkout validation | Invalid email, empty/stale/invalid cart, negative/boolean/string/over-limit quantities, missing Stripe key, accidental live-key configuration |
| Order creation | Database prices override tampered totals; pending status; item quantity/price snapshots; open-session reuse; frozen lost-response retry after renamed/reordered products; expiry renewal; complete-session waiting; missing webhook configuration; recoverable Stripe failure |
| Payment confirmation | Valid signed event; signature rejection; malformed payload; amount/currency/order/client-reference/mode mismatch; unpaid/unrelated events; async success; unknown Session ID requests retry; expired signature and signed malformed payload rejection; explicit test/live-mode flag required |
| Cart clearing | Return URL alone cannot confirm/clear; only paid purchases removed; duplicate webhook/return safe; new cart quantities preserved; next cart visit clears after delayed webhook; removed/re-added lines retained |
| Privacy/CSRF | Another browser cannot read a guest confirmation; checkout and cart require CSRF; only the signed webhook is exempt |
| Blog CRUD and permissions | Anonymous redirect; non-author direct GET/POST denied; author/staff edit/delete; GET deletion is non-destructive; server assigns author; invalid edit preserves original |
| Images | Existing Cloudinary image retained; explicit removal; valid image accepted/upload adapter saved; spoofed/non-image/GIF/oversized uploads rejected; failed upload reports error without changing stored post; missing Cloudinary name uses placeholders and permits text edit/clear |
| Newsletter | POST only; valid/normalised email; duplicate protection; 254-character model length enforced |
| Accounts | Signup/login with updated allauth; weak password rejected |
| Custom functionality | Own order history; other user's order/reorder denied; login required; paid-only POST reorder using current prices; historical total retained |
| Data migration | Two existing pre-Stripe orders receive distinct UUIDs and remain pending; purchased products protected from deletion; admin order deletion denied |
| Pages/SEO | Public page responses; internal navigation links; referenced local images exist; custom 404; robots and valid XML sitemap point to Render, include public blog detail and omit checkout |

The [actual final test output](evidence/django-tests.txt) and [direct-dependency advisory metadata](evidence/direct-dependency-advisories.json) are retained with this revision.

Test warnings that deliberately log a simulated Stripe connection failure or mismatched event are expected negative-path checks, not failed payments. No test sends a Stripe API request. The old `test_cloudinary.py` import-time network upload was removed; test discovery no longer has that side effect.

GitHub Actions workflow `.github/workflows/tests.yml` runs the isolated system/migration checks and tests on pushes and pull requests. The original workflow passed on PR #8. This review adds production-settings and manifest/static collection checks with an ephemeral CI-only secret; current commit results must be checked on the PR.

## Build and deployment checks

```bash
bash build.sh
python manage.py check --deploy --fail-level WARNING --settings=petwell.settings
```

The build was rerun during PR #8 review with the project virtualenv, local SQLite and development settings; dependency install, manifest/static collection and migrations succeeded. A first attempt correctly failed because the vendored Bootstrap bundle referenced an absent source map. The complete matching maps are now included; Bootstrap assets were verified against the npm tarball's SHA-512 integrity metadata and the build was rerun.

Deployment check outcomes are intentionally separate:

- Repository default with no deployment secret: **failed with `security.W009`**, warning about the development fallback `SECRET_KEY`. This is an outstanding configuration requirement, not a reason to silence the check.
- Production-style settings (`DEBUG=False`, Render host/URL, an ephemeral privately generated strong secret): **passed with no issues**. This does not validate the actual Render environment, database credentials, webhook endpoint, SMTP or Cloudinary account.
- Actual Render `check --deploy`: **not run**; owner must run it after secure configuration and approved deployment.

Direct dependency pins were checked against PyPI's version-specific published advisory metadata. Eight affected pins (Django, certifi, allauth, idna, Pillow, requests, sqlparse and urllib3) were updated to compatible versions with no active advisories listed at the time of the check. Django remains on 5.2 LTS. This is a point-in-time check of direct requirements, not a comprehensive audit of the operating system, build tools, CDN code or all possible vulnerabilities. Recheck before deployment.

## Local Chromium layout checks

Local browser checks use headless system Chromium via Playwright at **390×844**, **768×1024** and **1440×900**. They cover homepage, shop, blog, cart and checkout; mobile navigation; local image loading; horizontal overflow; CSRF-protected cart addition and the populated checkout form's missing-key error. No card data or external Stripe session is involved. Screenshots are local-development evidence, not proof of deployment or real integrations.

The initial check exposed reliance on external Bootstrap assets: Chromium could not validate that CDN connection in this environment, leaving the mobile menu inactive. The fix serves licensed, integrity-verified Bootstrap assets from the app; certificate verification was not disabled. See the final browser results linked below for the rerun outcome.

**Final local rerun: passed.** Fifteen page/viewport checks and three cart-to-checkout form flows passed. No horizontal overflow, broken images or JavaScript exceptions were detected in those checked states. Mobile/tablet menu expansion worked. The checkout correctly reported unavailable payments without configured keys and retained the cart. A first automation attempt used an incorrect exact label selector; the selector was corrected to the rendered field ID before the final run.

Actual local artifacts (27 October 2026, seeded development products; not deployed evidence):

- [Machine-readable browser results](evidence/local-browser-results.json)
- [Mobile shop](evidence/local-mobile-shop.png)
- [Desktop homepage](evidence/local-desktop-home.png)
- [Mobile checkout with missing-key error](evidence/local-mobile-checkout.png)

These screenshots do not show a Stripe success, a real marketing page or a production deployment. The remaining deployed acceptance matrix is still outstanding.

## Manual acceptance matrix — not yet passed on Render

Record date, browser/device, result, evidence file and any issue for each row. Do not mark a row passed because its automated counterpart passes.

| Check | Steps / expected result | Actual result |
| --- | --- | --- |
| Render startup | Review build/migration logs and `check --deploy`; PostgreSQL retains data across restart | TODO |
| Stripe test success | Complete a real hosted **sandbox** checkout; dashboard event reaches exact endpoint; matching order becomes paid only afterward | TODO |
| Card decline | Use Stripe's documented decline test card; no paid order, cart retained | TODO |
| Cancellation | Cancel hosted checkout; return to editable cart; pending order remains unpaid | TODO |
| Delayed/repeated webhook | Retry actual event in dashboard; one paid order/timestamp; refresh/next cart visit clears purchased quantities once | TODO |
| Return URL tampering | Different browser cannot read confirmation; pending return never means paid | TODO |
| Real Cloudinary images | Upload a small owned JPEG/PNG/WEBP; edit text without new image; remove/replace image; invalid file shows error; old post remains intact on upload outage | TODO |
| Blog access | Two accounts plus staff; direct edit/delete URL and POST attempts denied for non-owner; author/staff succeeds | TODO |
| Accounts | Register, login/logout, reset password with a verified SMTP sender; test invalid/weak credentials | TODO |
| My orders / Buy again | Account A sees A only; B cannot reorder A; update product price and reorder a paid order; cart uses new price, history retains old total | TODO |
| Newsletter | Valid and duplicate subscriptions; invalid email; no false campaign-delivery claim | TODO |
| Responsive navigation | Real mobile/tablet/desktop; keyboard and zoom; populated cart table; long blog titles/content; form errors; no inaccessible controls | TODO |
| SEO | Render robots and XML sitemap use Render host; public post entries resolve; no private/account checkout entries | TODO |
| Links and media | Check all navigation, product images and blog images on Render, including existing Cloudinary content and missing-image fallback | TODO |
| HTML/CSS validators | Validate representative rendered pages and CSS; keep actual reports, list remaining issues | TODO |
| Accessibility | Keyboard-only journey, focus visibility, labels, alt text, contrast and real Lighthouse report | TODO |
| Cross-browser | Chrome/Firefox/Safari or available equivalent; record actual versions and devices | TODO |
| Marketing | Verify published Facebook page and genuine posts, then add real URLs/evidence; a legacy mockup is not proof | TODO |

Known scope: no refunds, inventory, shipping/tax calculations, guest order claiming or automatic paid-order emails. Assess those limits against your product catalogue and supplied assessment feedback. Do not use real cards for acceptance testing.


## PR #8 review additions

The baseline 46 tests passed. Two new offline regressions then **failed on the original PR code**: a renamed product changed an idempotent Stripe retry payload, and delayed confirmation removed a newly re-added cart line. Both now pass with the fixes. Other added tests cover expiry/recovery, no duplicate session when completion awaits a webhook, missing webhook configuration, stale signatures, signed malformed events, the safe legacy-attempt upgrade path, order admin deletion, missing Cloudinary configuration and overlong newsletter emails.

The saved local screenshots above are from the initial implementation. They were not recaptured for this review and do not prove the deployed site or Stripe integrations work. See [PR8_REVIEW.md](PR8_REVIEW.md) for findings and merge prerequisites.
