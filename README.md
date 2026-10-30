# PetWell — pet wellness shop and community

PetWell is a Django e-commerce portfolio project for Code Institute Portfolio Project 5. Visitors can browse products and community posts, maintain a cart and pay through Stripe Checkout. Signed-in users can publish and manage their own posts, view their order history and buy the same products again at current prices.

For the remaining acceptance/submission actions, use the [current owner checklist](docs/OWNER_RELEASE_CHECKLIST.md) and [deployment evidence record](docs/evidence/30oct-production-deployment.md).

Deployment: **https://petwell-u0cr.onrender.com**. On **30 October 2026**, the owner verified deployment of **`f75dbe1c6fb9c16f3895a5b01451e2de4d9b9160`**, a successful build and all six project migrations. The owner subsequently verified the public shop/cart and one successful **GBP 11.49 Stripe sandbox Checkout**, with its Session complete/paid and related production order paid. Auto-deploy is disabled. The earlier maintenance-enabled report was the deployment snapshot; no current setting was independently inspected. These checks do not establish all provider/browser acceptance, and later PR changes are not claimed as deployed. PR #8 has not been merged by this documentation work.

**Completed:** deployed-commit CI (SQLite **189 passed + one PostgreSQL-only skip**, PostgreSQL **190 passed**); an independently executed real-backup PostgreSQL 18.6 rehearsal of all six migrations, preserving original records and leaving no pending migrations; owner-verified production build/migration success. [Sources and exact verification boundaries](docs/evidence/30oct-production-deployment.md). The earlier 29 October owner Mac rehearsal remains genuine historical evidence; neither it nor the later successful rehearsal needs repeating by default.

**Remaining:** owner-confirmed live product images show fallback despite ten stored references; the original Calming Lavender Spray URL now owner-verifiably displays construction artwork. Exact HTTP status and other products' asset content remain unverified. Detailed webhook/replay/cart/failure acceptance, SMTP, Cloudinary upload/rendering and broader live browser/security/SEO checks, offer/rights decisions and final evidence remain outstanding. **Do not claim complete end-to-end readiness from the completed deployment and single sandbox success.** This update grants no new production/provider/maintenance/payment action. [Configuration checks](docs/RENDER_CHECKLIST.md); [recovery runbook](docs/RELEASE_RUNBOOK.md).

Resubmission deadline: **31 October 2026, 12:00 noon Irish and UK time (GMT)**. The focus is a working, testable submission. A private feedback summary supplied by the owner guides this review. The private correspondence is not published; the official assessment guide was not available in the checkout. The evidence map is not an assessor decision.

## Features and user stories

| User | Story | Implementation / acceptance check |
| --- | --- | --- |
| Visitor | Browse products with clear prices | Shop, database prices, local missing-image fallback |
| Customer | Add and remove products safely | Session cart, POST actions, CSRF protection, quantity cap |
| Customer | Pay securely without exposing card details | Hosted Stripe Checkout; server-calculated GBP amount |
| Customer | See an accurate payment result | Pending order until verified signed webhook; return URL cannot mark paid |
| Customer | Keep cart on cancellation or payment failure | No cart clearing before payment; recoverable errors |
| Member | Manage my pets and everyday care reminders | Private PetProfile CRUD, validation, server-side ownership and focus-specific routine prompt |
| Member | See only my orders and buy again | Login-protected order history; owner-only POST reorder at current prices |
| Reader | Read full blog articles | Linked list/detail views and public sitemap entries |
| Author | Create, edit and delete my posts | Server-side ownership checks for GET and POST; delete confirmation |
| Staff | Moderate community posts | Staff may edit/delete posts; non-staff cannot change another author's post |
| Author | Upload a valid optional image | Actual image decoding, JPEG/PNG/WEBP allowlist, 5 MB limit; retain/remove existing image |
| Visitor | Subscribe once with a valid email | Validated, normalised database subscription; no claim of marketing delivery |

### Custom functionality and data model

The application models are `Product`, `Order`, `OrderItem`, `BlogPost`, `Subscriber` and `PetProfile`, plus the internal `CheckoutState` coordinator, alongside Django/allauth users; see the [current schema diagram](docs/MODELS.md). **My pets** (`/pets/`) is a distinct member feature: add a name/species/care focus and optional notes, view a routine reminder, edit the profile or confirm deletion. Profiles are private to their owner, including direct form URLs; staff do not receive access to another member's care notes. These are planning reminders, not veterinary advice.

Order history and **Buy again** extend the commerce models into a customer-facing repeat-purchase workflow. Historical totals and item prices remain unchanged; reordered products use current prices. Only the purchaser can access/reorder their paid orders. Guest orders remain tied to their browser session and are not automatically claimed by email.

`Order` now has a unique public UUID, pending/paid status, unique Stripe Checkout Session ID and payment timestamp, plus the frozen Stripe creation payload and cart-line identities (neither contains credentials). `Product.is_available` withdraws an explicitly reviewed offer from catalogue/cart/checkout/reorder without deleting history. Existing products default to available; an authorised operator must separately verify and change the actual PDF row. `OrderItem` protects referenced products from deletion so historical purchases are preserved. Existing pre-Stripe orders migrate to **pending** because there is no payment evidence for them. Do not manually relabel them as paid.

## Technology

Python 3.11; Django 5.2.17; Stripe Python SDK 12.5.1; PostgreSQL on Render (SQLite locally); Cloudinary image fields; WhiteNoise static files; Bootstrap 5.3.8 (vendored CSS/JS with MIT license); django-allauth. Security-affected direct pins were updated against PyPI advisory metadata on 27 October 2026; see TESTING.md for scope. Exact direct dependency versions are in `requirements.txt`. There is no JavaScript build step.

## Local installation

Use the existing checkout in an isolated cloud task; no extra Git worktree is necessary.

```bash
git clone --branch fix/pp5-resubmission https://github.com/bobes81/Petwell.git
cd Petwell
python3.11 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=petwell.settings
export DEBUG=True
export SITE_URL=http://localhost:8000
export ALLOWED_HOSTS=localhost,127.0.0.1
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# Fresh local-only secret; keep it stable in your private environment if
# testing password-reset links across server restarts.
export SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
# Keep DATABASE_URL unset locally unless you deliberately select a local DB.
unset DATABASE_URL
python manage.py migrate
python manage.py shell -c 'from products.seed import run; run()'
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver
```

On Windows PowerShell, after cloning the same branch and opening the checkout:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_SETTINGS_MODULE = "petwell.settings"
$env:DEBUG = "True"
$env:SITE_URL = "http://localhost:8000"
$env:ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
$env:SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
python manage.py migrate
python manage.py shell -c "from products.seed import run; run()"
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver
```

These are instructions, not a claim that Windows was tested here. The Linux/cloud workflow was exercised locally. The repeatable seed creates nine sample physical-product listings without images and preserves existing records/prices/images. It no longer creates the unsupported PDF download; it does not remove an existing one. Do not load `fixtures/products.json` expecting data: it is currently empty. Create products through admin or use the seed only on a disposable development database, never as a production migration step.

The app reads the **process environment**. It does not automatically load `.env`; if using that file, use your shell/IDE's secure environment loader. `.env` is ignored. Never commit keys. Local console email prints messages to the developer terminal and does not deliver them.

For offline tests (no external credentials required):

```bash
python manage.py test --settings=petwell.test_settings
```

Default test settings always use an isolated in-memory SQLite database and in-memory email backend, not a configured production database. Stripe and Cloudinary upload calls in tests are mocked. The public Cloudinary cloud name used in tests is a dummy for URL rendering, not an account credential.

CI runs the suite against disposable PostgreSQL 16 and 18 services with `petwell.postgres_test_settings` and `TEST_DATABASE_URL`. The original `postgres` check name is retained for 16; 18 uses `postgres-18`. This test-only module must never serve the app or point to a production/valuable restored database. The PostgreSQL-specific overlapping-worker test is explicitly skipped on local SQLite; report the backend and skip count rather than treating it as a local concurrency pass.

For the owner's restored local database, use [petwell.rehearsal_settings](docs/RESTORED_DB_REHEARSAL.md), which requires private `REHEARSAL_DATABASE_URL` and a separate `REHEARSAL_SECRET_KEY`. It has no production URL fallback, rejects remote/routing-override targets, permits local PostgreSQL without forcing SSL and disables Stripe/Cloudinary/SMTP. Keep automated tests separate from this restored-copy workflow. Never use this profile on Render; production database SSL remains required.

## Environment variables

| Name | Purpose / value |
| --- | --- |
| `SECRET_KEY` | Strong unique Django secret; required for deployment. Generate privately, e.g. with Django's `get_random_secret_key()`; do not paste into README or chat. The fallback is for development and triggers a deployment warning. |
| `DEBUG` | `True` locally, **`False` on Render** (case-sensitive). |
| `ALLOWED_HOSTS` | Comma-separated hostnames. Render: `petwell-u0cr.onrender.com`; add a custom hostname only if actually configured. No schemes. |
| `SITE_URL` | Local: `http://localhost:8000`; Render: `https://petwell-u0cr.onrender.com`. Used for Stripe return URLs, CSRF origin and SEO. |
| `DATABASE_URL` | Render PostgreSQL connection URL. Production must use persistent PostgreSQL; SQLite on an ephemeral Render filesystem loses data. Existing parser requires SSL. |
| `STRIPE_SECRET_KEY` | Stripe sandbox/test secret (`sk_test_...`) for assessment. Never expose in templates or client code. |
| `STRIPE_WEBHOOK_SECRET` | Signing secret (`whsec_...`) for the exact Stripe endpoint. A CLI listener has a different secret from a dashboard endpoint. |
| `STRIPE_LIVE_MODE` | Keep **`False`** for assessment. A live key is rejected unless explicitly enabled. Do not enable live payments without owner approval. |
| `CLOUDINARY_URL` | Supported existing Render configuration. The Cloudinary SDK reads the full private URL to configure the cloud name and upload credentials; separate Cloudinary variables are unnecessary. Treat the whole URL as a secret. |
| `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Optional alternative to `CLOUDINARY_URL`. Use one source: when `CLOUDINARY_CLOUD_NAME` is set, the SDK prefers the separate variables. All three are needed for uploads in that configuration. |
| `EMAIL_BACKEND` | Default console backend. For delivery: `django.core.mail.backends.smtp.EmailBackend`. |
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP server/port. Gmail: `smtp.gmail.com`, `587`. Legacy defaults: SendGrid, `587`. |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Gmail STARTTLS: `True`, `False`. Both cannot be true. SSL on 465 requires TLS false explicitly. |
| `EMAIL_HOST_USER` | Gmail: `petwell.shop.uk@gmail.com`; legacy SendGrid default: `apikey`. |
| `EMAIL_HOST_PASSWORD` | Private provider credential, e.g. an eligible Google App Password. Never the normal Google sign-in password; never commit a value. |
| `EMAIL_TIMEOUT` | Positive timeout in seconds, default `10`. |
| `SENDGRID_API_KEY` | Legacy password fallback only for `smtp.sendgrid.net` when `EMAIL_HOST_PASSWORD` is unset. Never reused for Gmail. |
| `DEFAULT_FROM_EMAIL` | Gmail: `PetWell <petwell.shop.uk@gmail.com>`; otherwise an authorised/verified sender for the chosen provider. Do not use the example default in production. |

The existing Render variable names reported by the owner are `CLOUDINARY_URL`, `DATABASE_URL`, `DEBUG` and `SECRET_KEY`. This revision supports that Cloudinary URL directly and preserves it when the storage package loads. Copy the exact private value from your secure provider configuration; do not print it or include it in screenshots. Image delivery uses HTTPS. Without Cloudinary configuration, local placeholders remain available. These are configuration compatibility checks, not verification of the existing production values or an actual upload.

Hosted Stripe Checkout does not require a publishable key or Stripe.js in this app. The old `STRIPE_WH_SECRET` name is unused; use `STRIPE_WEBHOOK_SECRET`. SMTP now supports `EMAIL_HOST_PASSWORD` directly; existing SendGrid fallback remains compatible. The four existing variable names do not by themselves configure Stripe or email delivery: checkout stays unavailable without the API/signing keys, and email defaults to the console. Keep Render's `DJANGO_SETTINGS_MODULE` as `petwell.settings`, never `petwell.test_settings` or a cloud-only helper module.

## Catalogue images and legacy PDF

**Live image issue, 30 October:** owner confirms ten stored references and placeholder artwork. For Calming Lavender Spray, opening the original Cloudinary URL displays the construction/coming-soon graphic, not the intended illustration; exact HTTP status was not captured. [The owner-approved replacement plan](docs/CATALOGUE_PLACEHOLDER_REPLACEMENT.md) prepares correct new/reused assets and guarded image-only updates, preserving IDs/prices/orders/old assets. The deployed app already supports the nine concept references and AI captions, so this data-only correction needs no new application deploy. Uploads and production mapping still require explicit approval and have not been executed. The earlier raw-string helper fix is separate from this wrong-artwork finding.


For 30 October, use the [step-by-step owner cutover/rollback plan](docs/RELEASE_2026-10-30.md), [iPad/MacBook guide](docs/IPAD_MACBOOK_CHECKLIST.md) and [final Pass evidence matrix](docs/PASS_COMPLIANCE_MATRIX.md). The conditional decision to withdraw the verified undeliverable PDF is approved; the [guarded exact-row procedure](docs/LEGACY_PDF_WITHDRAWAL.md) requires separate production access/write approval and preserves all history. Actual production withdrawal remains unverified in this record; verify the intended row and obligations privately.

[The safe image workflow](docs/CATALOGUE_IMAGES.md) and [blank nine-item manifest](docs/catalogue-images.example.json) prepare explicit association of owner-supplied AI illustrations with existing physical products. The owner supplied nine 1000×1000 PNG concept illustrations; [unchanged originals, measured hashes and draft](docs/catalogue/README.md) are now reviewed locally. The owner subsequently supplied actual metadata for nine new Cloudinary uploads; the repository workflow did not upload or assign them. Remote artwork and current production assignment remain unverified here. Use the separately approved [guarded replacement workflow](docs/CATALOGUE_PLACEHOLDER_REPLACEMENT.md) for existing non-empty references. Its `--sources-only` mode validates the incomplete source draft without database/provider access. Full mapping checks exact product identities and Cloudinary metadata, defaults to dry-run and fills only empty image references after explicit `--apply`. It never uploads assets, creates products or overwrites existing images/prices/descriptions. The supplied PNG artwork embeds its own AI/concept disclosure, which is preserved in full by contain fitting. The current PR removes the duplicate HTML caption beneath product images; this presentation change requires a separately approved application deploy and is not yet live. This is a tool for a later approved operation, not evidence that production images are fixed.

The supplied feedback identifies placeholders, without requiring photographic media. Review actual AI images for accuracy/rights and label them honestly; final assessment acceptance is not guaranteed. The legacy PDF is not a tenth target: preserve its records and either verify actual manual delivery or arrange complete withdrawal before enabling payments. Hiding only its shop card would leave cart/reorder paths open. The owner verified successful production application of `products.0002_product_is_available` with the other five project migrations on 30 October; it defaults existing rows to available and does not automatically archive the PDF. Actual production withdrawal remains unverified.

For Gmail, the [Render SMTP checklist](docs/RENDER_CHECKLIST.md#smtp--delivery-is-not-enabled-by-the-four-reported-variables) lists the environment-only profile and remaining account/egress/received-email checks. App Password availability and outbound Render SMTP must be genuinely verified without buying resources. Offline configuration tests do not prove delivery.

## Checkout and payment lifecycle

1. Validate customer name/email/address and each cart quantity/product. Read all prices from the database; ignore client-supplied totals.
2. Acquire a short database checkout lease for the browser session so overlapping workers use one durable active-order pointer. Save a pending order and item-price snapshot atomically before Stripe I/O. The complete Stripe creation payload is saved before the API request. Lost-response retries reuse the exact payload and idempotency key, including product labels and line order. Existing sessions are retrieved before considering changed cart/contact data: unchanged open sessions are reused; a superseded open session must be confirmed expired before replacement; completed sessions wait for their webhook. Confirmed expired sessions get a new order/key while the old mapping remains intact. Ambiguous expiration fails closed. The lease expires after 120 seconds if a worker dies; requests use a bounded 10-second Stripe timeout and preserve durable recovery data.
3. Create a card-only, GBP Stripe Checkout Session and redirect to Stripe. No card data passes through PetWell.
4. Only a correctly signed `checkout.session.completed` or `checkout.session.async_payment_succeeded` event can set `paid`. Its Session ID, order UUID, client reference, total, currency, payment mode, paid status and live/test mode must match. Duplicate events do not change the original `paid_at` timestamp.
5. The return page displays pending until that confirmation arrives. It cannot mark an order paid, even if its URL is copied. Guest confirmation requires the original checkout browser session.
6. On the return page or next cart/checkout visit, subtract purchased quantities once. Additional cart quantities are kept. Each cart line has an identity that changes when removed and re-added, so delayed confirmation cannot remove a newly added line. A webhook cannot directly change a browser's session cookie; cart reconciliation occurs on a subsequent browser request.

Checkout is disabled until both the Stripe API key and webhook signing secret are configured. Cancellation, failed cards and Stripe connection errors keep the cart. Pending orders are not fulfilled and may remain in history after abandoned payment. A delayed webhook is retried by Stripe; a session not yet stored locally returns 503 to request retry. Do not fulfill orders based on a browser screenshot or return URL.

If a create response was lost and the saved attempt still has no Stripe Session ID after **23 hours**, automatic retry is held for review. Stripe idempotency keys are not permanent; blindly repeating an old create could produce another payable Session. The order, exact payload and cart remain intact, including when contact/cart details change. An operator must reconcile the original attempt through an approved provider procedure; do not create a replacement or mark it paid manually. Known Session IDs remain retrievable regardless of age. The 23-hour guard is conservative, not evidence that a payment failed or succeeded.

The in-app paid result and account history are payment confirmation. Automatic order-confirmation email dispatch is deliberately not part of the webhook: SMTP availability cannot determine whether an order is paid. Welcome/password-reset email can use Gmail SMTP or an already configured alternative when genuinely verified. Newsletter subscriptions are stored; no campaign automation is implemented. Refunds, tax/shipping rules, inventory and fulfilment automation are outside this revision.

## Render deployment — manual, owner-controlled

**Completed on 30 October:** the owner verified deployment of `f75dbe1c6fb9c16f3895a5b01451e2de4d9b9160`, build and six migrations. Later owner checks confirmed public shop/cart and one sandbox success; the initial maintenance-enabled snapshot is not a new setting inspection. [Current evidence](docs/evidence/30oct-production-deployment.md). The following is the retained procedure for a future separately approved release, not an instruction to redeploy or reapply migrations now. A future deployment requires a fresh suitable backup and review of the selected code/schema pair.

Use the [Render compatibility and release checklist](docs/RENDER_CHECKLIST.md) for the existing four-variable setup, additional test-payment/email requirements, backup and migration sequence, and the acceptance checks that remain unverified. The [release and recovery runbook](docs/RELEASE_RUNBOOK.md) covers abort decisions, partial migration failure and preserving order/Stripe mappings before any approved database restoration. A backup does not undo provider payments or invalidate already issued Checkout URLs.

1. Review the existing Render Python service's GitHub connection. Select the reviewed branch/commit only when ready to deploy. Use the repository's `.python-version` (3.11) with a supported patch runtime. Confirm Render's runtime in build logs.
2. Reuse the existing persistent Render PostgreSQL database and secure configuration. Verify `DATABASE_URL`, `SECRET_KEY`, `DEBUG=False` and the existing `CLOUDINARY_URL`; no separate Cloudinary credentials are required. Verify the Render hostname/URL (their defaults match this target), then configure sandbox Stripe and SMTP only when approved. Do not use local/test settings or create an additional paid resource for this checklist.
3. Before a release, review the complete `python manage.py showmigrations`/`python manage.py migrate --plan` output and take a recoverable PostgreSQL backup. Coordinate an approved write-pause/cutover: old `orders.0001` workers cannot insert orders after the required new fields are added. The orders migration assigns distinct UUIDs and keeps old orders pending; `0004` adds immutable payment/cart snapshots. `orders.0005` adds the checkout coordinator and `accounts.0001` adds private pet profiles. The later `products.0002_product_is_available` was not part of the earlier five-migration owner rehearsal; it is now covered by the completed six-migration real-backup rehearsal and owner-verified production deployment. Do not repeat these completed stages. Choose one reviewed migration stage: the existing build command `bash build.sh` already installs requirements, collects static assets and runs `python manage.py migrate --noinput`; a separate manual migration first is unnecessary. It is not a read-only production check. A separate migration/pre-deploy stage is optional only if already supported by the existing plan, with dependency installation/static collection as the build command; it still requires the same approved write pause. Do not fake, skip or edit applied migrations. Do not blindly downgrade the schema or switch to old code afterward: reverse migrations remove payment metadata. Review recovery against the verified backup and matching code.
4. Start command: `gunicorn petwell.wsgi:application --bind 0.0.0.0:$PORT`.
5. Run `python manage.py check --deploy --fail-level WARNING` with the actual Render configuration. A passing check is not proof that PostgreSQL, Cloudinary, SMTP or Stripe credentials work; validate them separately.
6. Use the existing authorised admin account. Only if none exists, separately approve creating one securely with `python manage.py createsuperuser`. Review existing catalogue records/prices; associate approved images with the guarded workflow rather than recreating products or seeding production. Optionally review the Django Sites hostname for account email branding.
7. Configure the Stripe sandbox endpoint below. Run the manual acceptance matrix in [docs/TESTING.md](docs/TESTING.md) and capture genuine results before submission.

HTTPS redirection, secure cookies, HSTS and the trusted proxy header are enabled outside DEBUG. `SITE_URL` must be HTTPS in production. WhiteNoise uses Django 5's `STORAGES` configuration. Password validators and explicit allowed hosts are enabled. The protected payment fields in admin cannot be manually marked paid, and order deletion is disabled to preserve payment and fulfilment records.

## Stripe configuration and test-only acceptance

In the correct **Stripe sandbox/test account**, create a webhook destination:

`https://petwell-u0cr.onrender.com/checkout/webhook/`

Subscribe to **`checkout.session.completed`** and **`checkout.session.async_payment_succeeded`**. Set that endpoint's signing secret as `STRIPE_WEBHOOK_SECRET` in Render. Keep `STRIPE_SECRET_KEY` in the same test account and `STRIPE_LIVE_MODE=False`. Do not use a live key or a real card for portfolio testing.

After an explicitly approved deployment, create a genuine test checkout using a product from the site. On Stripe's hosted sandbox page use Stripe's documented test card `4242 4242 4242 4242`, a future expiry and any valid test CVC/postcode. Check a failed test card such as `4000 0000 0000 0002` separately. Check the dashboard delivery response and correlate the saved Session ID and public order reference. A generic dashboard sample event cannot pay an unrelated real order because references and totals must match.

For local integration, if Stripe CLI is installed and authenticated in the test account:

```bash
stripe listen --events checkout.session.completed,checkout.session.async_payment_succeeded --forward-to localhost:8000/checkout/webhook/
```

Use the listener's signing secret locally. Complete a **test** hosted checkout. Offline automated signature tests validate the application logic but do not replace this dashboard-to-app end-to-end check. Test-mode dashboard access and deployment credentials must be supplied securely by the owner; no secrets belong in evidence screenshots.

## Testing and evidence

See [docs/TESTING.md](docs/TESTING.md) for reproducible commands, actual results and the outstanding manual matrix. See [docs/EVIDENCE.md](docs/EVIDENCE.md) for the screenshot, wireframe and marketing checklist. These documents distinguish automated results from work that has not been performed.

No W3C, Lighthouse, cross-browser, accessibility, real email or live payment pass is claimed without a recorded run. [Asset inspection and catalogue-image checklist](docs/ASSETS.md) record what the legacy images actually show and which seeded products still need accurate authorised images and source records. The old file named Facebook mockup is a watermarked title card, not a Facebook-page design or published-page evidence.

A new [Facebook-page design proposal](docs/marketing/facebook-mockup.html) and [its genuine local rendering](docs/marketing/facebook-mockup.png) are labelled **retrospective mockup, created 28 October 2026, not published**. It is a design artifact, not proof of a live page, customer engagement or a campaign. Open the HTML locally to inspect the layout. The supplied feedback explicitly permits this clearly labelled mockup format; a published page or marketing metrics are not added as submission blockers.

## UX, SEO and business purpose

PetWell's B2C shop pairs wellness products with community articles. The intended conversion path is homepage → shop → cart → secure hosted payment → confirmed order; returning customers use My orders → Buy again. The responsive Bootstrap navigation, labelled forms, keyboard skip link, inline validation, delete confirmation, readable empty states and local placeholder image support this path.

`/robots.txt` names the Render sitemap and discourages indexing of private/account/cart/checkout routes. Robots rules are not access control. `/sitemap.xml` contains the homepage, shop, blog list and existing public blog posts using the configured deployment domain. Navigation now links to full blog articles. Placeholder social account links were removed until the real marketing pages are verified. Public pages now have page-specific metadata and canonical URLs without query parameters; private pages have noindex metadata and no public canonical.

Planned marketing: maintain an authentic Facebook business page, publish real product/community posts and use consented newsletter subscriptions. No marketing reach, conversion statistics or active campaign delivery is claimed. Replace planning statements with dated evidence only after actually doing the work.

## Design artifacts

These are new **retrospective design reviews created 28 October 2026**, not invented pre-development planning. [Editable wireframes and captions](docs/design/README.md) describe six actual workflows; the [ER diagram](docs/MODELS.md) reflects the current database schema.

<details>
<summary>Retrospective wireframes — local diagram render, not application evidence</summary>

![Retrospective desktop wireframes created 28 October 2026](docs/design/wireframes-desktop.png)

</details>

<details>
<summary>Facebook-page design proposal — explicitly not published</summary>

![Local rendering of the clearly labelled Facebook-page proposal, not a live page](docs/marketing/facebook-mockup.png)

</details>

## Assessment status

[Assessment review](docs/ASSESSMENT_REVIEW.md) maps the requested areas to actual models, screens, tests and remaining evidence. The owner supplied a private assessment summary on 28 October; the original correspondence is not published and the official full guide was not available here. The mapping must not be presented as an official assessor sign-off.

## Known issues and submission work remaining

- One real sandbox Checkout for GBP 11.49, complete/paid Session and paid production order are owner verified. Detailed webhook destination/replay/cart/failure checks, Cloudinary upload/delivery and received SMTP reset email remain unverified. The live image fallback is a confirmed owner-reported issue; do not assume missing assets without the original URL/response.
- Existing orders without Stripe evidence stay pending. Never fulfil/relabel them based on historical assumptions. Pre-fix attempts with no Session ID or saved payload get a fresh order/key. For legacy orders without cart-line identities, automatic cart subtraction is skipped to preserve potentially new items; review/clear that cart manually.
- Paid order history protects referenced products from deletion; edit a product instead of deleting it when it appears in an order.
- Card-only GBP checkout has no stock control, shipping charges, taxes, refunds or automated fulfilment. Review whether your actual product catalogue is suitable for this scope.
- New development seeding omits the unsupported "Mindful Pet Journal (PDF)" download. Existing/restored rows remain untouched. If that listing is still offered, provide the actual file and a verified manual fulfilment process, or remove the offer before accepting payment. A paid order does not deliver a file automatically. Products referenced by historical order items are protected from deletion; preserve those records instead of deleting order history to remove a listing.
- Guests must retain the checkout browser session to view confirmation. Guest purchases are not attached to an account by matching email.
- Real Cloudinary assets still require browser/network checks on the deployed site. Bootstrap CSS/JS is served locally rather than depending on a CDN.
- Historical duplicate/backup templates and settings remain in the repository; active settings are `petwell/settings.py`, and project-level `templates/` takes precedence over app templates.
- Retrospective wireframes, a Facebook-page design mockup, local screenshots and an assessment evidence map are included. Actual deployed screenshots, outstanding accessibility/browser checks and source/rights records remain owner tasks. Earlier local Nu validation results retain their recorded scope. The supplied feedback permits the clearly labelled Facebook mockup; no published page is claimed or newly required. Do not submit placeholders as completed evidence.

## Credits and authorship

### AI Tools

AI tools, including ChatGPT and OpenAI Codex, were used to support the development, debugging, testing, documentation, and improvement of this project.



Original repository: [bobes81/Petwell](https://github.com/bobes81/Petwell). Third-party packages and Bootstrap provide the framework/components identified above. Product descriptions, images and article content require owner review for accuracy, permission and attribution. No license or asset rights are assumed where none are recorded.
