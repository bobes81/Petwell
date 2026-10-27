# PetWell — pet wellness shop and community

PetWell is a Django e-commerce portfolio project for Code Institute Portfolio Project 5. Visitors can browse products and community posts, maintain a cart and pay through Stripe Checkout. Signed-in users can publish and manage their own posts, view their order history and buy the same products again at current prices.

Deployment target: **https://petwell-u0cr.onrender.com**. This branch has not been deployed or merged. The target URL is not a claim that the latest changes are live.

Resubmission deadline: **31 October 2026, 12:00 UK time (GMT)**. The focus is a working, testable submission. Assessment compliance must be checked against the actual rubric and assessor feedback; neither was supplied for this revision.

## Features and user stories

| User | Story | Implementation / acceptance check |
| --- | --- | --- |
| Visitor | Browse products with clear prices | Shop, database prices, local missing-image fallback |
| Customer | Add and remove products safely | Session cart, POST actions, CSRF protection, quantity cap |
| Customer | Pay securely without exposing card details | Hosted Stripe Checkout; server-calculated GBP amount |
| Customer | See an accurate payment result | Pending order until verified signed webhook; return URL cannot mark paid |
| Customer | Keep cart on cancellation or payment failure | No cart clearing before payment; recoverable errors |
| Member | See only my orders and buy again | Login-protected order history; owner-only POST reorder at current prices |
| Reader | Read full blog articles | Linked list/detail views and public sitemap entries |
| Author | Create, edit and delete my posts | Server-side ownership checks for GET and POST; delete confirmation |
| Staff | Moderate community posts | Staff may edit/delete posts; non-staff cannot change another author's post |
| Author | Upload a valid optional image | Actual image decoding, JPEG/PNG/WEBP allowlist, 5 MB limit; retain/remove existing image |
| Visitor | Subscribe once with a valid email | Validated, normalised database subscription; no claim of marketing delivery |

### Custom functionality and data model

The existing models are `Product`, `Order`, `OrderItem`, `BlogPost` and `Subscriber`, alongside Django/allauth users; see the [current schema diagram](docs/MODELS.md). Order history and **Buy again** extend these models into a customer-facing repeat-purchase workflow. Historical totals and item prices remain unchanged; reordered products use current prices. Only the purchaser can access/reorder their paid orders. Guest orders remain tied to their browser session and are not automatically claimed by email.

`Order` now has a unique public UUID, pending/paid status, unique Stripe Checkout Session ID and payment timestamp, plus the frozen Stripe creation payload and cart-line identities (neither contains credentials). `OrderItem` protects referenced products from deletion so historical purchases are preserved. Existing pre-Stripe orders migrate to **pending** because there is no payment evidence for them. Do not manually relabel them as paid.

## Technology

Python 3.11; Django 5.2.17; Stripe Python SDK 12.5.1; PostgreSQL on Render (SQLite locally); Cloudinary image fields; WhiteNoise static files; Bootstrap 5.3.8 (vendored CSS/JS with MIT license); django-allauth. Security-affected direct pins were updated against PyPI advisory metadata on 27 October 2026; see TESTING.md for scope. Exact direct dependency versions are in `requirements.txt`. There is no JavaScript build step.

## Local installation

Use the existing checkout in an isolated cloud task; no extra Git worktree is necessary.

```bash
git clone https://github.com/bobes81/Petwell.git
cd Petwell
python3.11 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=petwell.settings
export DEBUG=True
export SITE_URL=http://localhost:8000
export ALLOWED_HOSTS=localhost,127.0.0.1
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# Set SECRET_KEY securely in your shell or environment settings.
python manage.py migrate
python manage.py shell -c 'from products.seed import run; run()'
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver
```

On Windows, activate with `venv\Scripts\activate` and configure environment variables using PowerShell. The product seed is repeatable. Do not load `fixtures/products.json` expecting data: it is currently empty. Create products through admin or use the seed.

The app reads the **process environment**. It does not automatically load `.env`; if using that file, use your shell/IDE's secure environment loader. `.env` is ignored. Never commit keys. Local console email prints messages to the developer terminal and does not deliver them.

For offline tests (no external credentials required):

```bash
python manage.py test --settings=petwell.test_settings
```

Test settings always use an isolated in-memory SQLite database and in-memory email backend, not a configured production database. Stripe and Cloudinary upload calls in tests are mocked. The public Cloudinary cloud name used in tests is a dummy for URL rendering, not an account credential.

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
| `CLOUDINARY_CLOUD_NAME` | Your public Cloudinary cloud name; needed to render stored Cloudinary images. |
| `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Cloudinary upload credentials, configured securely on Render. |
| `EMAIL_BACKEND` | Default console backend. For delivery: `django.core.mail.backends.smtp.EmailBackend`. |
| `SENDGRID_API_KEY` | SMTP password for SendGrid if SMTP backend is selected. |
| `DEFAULT_FROM_EMAIL` | A sender address you have verified in SendGrid. Do not use the default example address in production. |

Hosted Stripe Checkout does not require a publishable key or Stripe.js in this app. Old README names `STRIPE_WH_SECRET`, `EMAIL_HOST_PASSWORD` and `CLOUDINARY_URL` are not used by the current settings; configure the names above. Keep Render's `DJANGO_SETTINGS_MODULE` as `petwell.settings`, never `petwell.test_settings` or a cloud-only helper module.

## Checkout and payment lifecycle

1. Validate customer name/email/address and each cart quantity/product. Read all prices from the database; ignore client-supplied totals.
2. Save a pending order and item-price snapshot atomically. The complete Stripe creation payload is saved before the API request. Lost-response retries reuse the exact payload and idempotency key, including product labels and line order. Existing sessions are retrieved: open sessions are reused, completed sessions wait for their webhook, and confirmed expired sessions get a new order/key while the old mapping remains intact.
3. Create a card-only, GBP Stripe Checkout Session and redirect to Stripe. No card data passes through PetWell.
4. Only a correctly signed `checkout.session.completed` or `checkout.session.async_payment_succeeded` event can set `paid`. Its Session ID, order UUID, client reference, total, currency, payment mode, paid status and live/test mode must match. Duplicate events do not change the original `paid_at` timestamp.
5. The return page displays pending until that confirmation arrives. It cannot mark an order paid, even if its URL is copied. Guest confirmation requires the original checkout browser session.
6. On the return page or next cart/checkout visit, subtract purchased quantities once. Additional cart quantities are kept. Each cart line has an identity that changes when removed and re-added, so delayed confirmation cannot remove a newly added line. A webhook cannot directly change a browser's session cookie; cart reconciliation occurs on a subsequent browser request.

Checkout is disabled until both the Stripe API key and webhook signing secret are configured. Cancellation, failed cards and Stripe connection errors keep the cart. Pending orders are not fulfilled and may remain in history after abandoned payment. A delayed webhook is retried by Stripe; a session not yet stored locally returns 503 to request retry. Do not fulfill orders based on a browser screenshot or return URL.

The in-app paid result and account history are payment confirmation. Automatic order-confirmation email dispatch is deliberately not part of the webhook: SMTP availability cannot determine whether an order is paid. Welcome/password-reset email can use SendGrid when configured. Newsletter subscriptions are stored; no campaign automation is implemented. Refunds, tax/shipping rules, inventory and fulfilment automation are outside this revision.

## Render deployment — manual, owner-controlled

**No production deployment has been performed for this revision.** Before deployment, back up the existing database and confirm the selected branch/commit. Do not turn on automatic deployment while reviewing the branch.

1. Connect the GitHub repository to a Render Python web service. Select the reviewed branch/commit only when ready to deploy. Use the repository's `.python-version` (3.11) with a supported patch runtime. Confirm Render's runtime in build logs.
2. Attach a persistent Render PostgreSQL database and securely set the variables above, especially `DATABASE_URL`, `SECRET_KEY`, `DEBUG=False`, the Render hostname and sandbox Stripe keys. Do not use local/test settings.
3. Build command: `bash build.sh`. It installs requirements, collects static assets and applies migrations. If your Render plan supports a pre-deploy command, prefer `python manage.py migrate --noinput` there and run `pip install -r requirements.txt && python manage.py collectstatic --noinput` as the build command. Back up first whichever path you choose.
4. Start command: `gunicorn petwell.wsgi:application --bind 0.0.0.0:$PORT`.
5. Run `python manage.py check --deploy --fail-level WARNING` with the actual Render configuration. A passing check is not proof that PostgreSQL, Cloudinary, SMTP or Stripe credentials work; validate them separately.
6. Create an admin user securely using `python manage.py createsuperuser`. Add real product data/images and review current prices. Optionally set the Django Sites record to the Render hostname for account email links.
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

No W3C, Lighthouse, cross-browser, accessibility, real email or live payment pass is claimed without a recorded run. Existing image files and the Facebook mockup in `static/images/` are legacy assets whose provenance and currency must be checked before treating them as evidence.

## UX, SEO and business purpose

PetWell's B2C shop pairs wellness products with community articles. The intended conversion path is homepage → shop → cart → secure hosted payment → confirmed order; returning customers use My orders → Buy again. The responsive Bootstrap navigation, labelled forms, keyboard skip link, inline validation, delete confirmation, readable empty states and local placeholder image support this path.

`/robots.txt` names the Render sitemap and discourages indexing of private/account/cart/checkout routes. Robots rules are not access control. `/sitemap.xml` contains the homepage, shop, blog list and existing public blog posts using the configured deployment domain. Navigation now links to full blog articles. Placeholder social account links were removed until the real marketing pages are verified.

Planned marketing: maintain an authentic Facebook business page, publish real product/community posts and use consented newsletter subscriptions. No marketing reach, conversion statistics or active campaign delivery is claimed. Replace planning statements with dated evidence only after actually doing the work.

## Known issues and submission work remaining

- End-to-end Stripe sandbox payments, Render webhook delivery, real Cloudinary uploads and SendGrid email require owner configuration and manual validation; no external integration pass is claimed yet.
- Existing orders without Stripe evidence stay pending. Never fulfil/relabel them based on historical assumptions. Pre-fix attempts with no Session ID or saved payload get a fresh order/key. For legacy orders without cart-line identities, automatic cart subtraction is skipped to preserve potentially new items; review/clear that cart manually.
- Paid order history protects referenced products from deletion; edit a product instead of deleting it when it appears in an order.
- Card-only GBP checkout has no stock control, shipping charges, taxes, refunds or automated fulfilment. Review whether your actual product catalogue is suitable for this scope.
- Guests must retain the checkout browser session to view confirmation. Guest purchases are not attached to an account by matching email.
- Real Cloudinary assets still require browser/network checks on the deployed site. Bootstrap CSS/JS is served locally rather than depending on a CDN.
- Historical duplicate/backup templates and settings remain in the repository; active settings are `petwell/settings.py`, and project-level `templates/` takes precedence over app templates.
- Wireframes, dated browser screenshots, external HTML/CSS/accessibility reports, assessor mapping and real Facebook marketing evidence remain owner tasks. Do not submit placeholders as completed evidence.

## Credits and authorship

Original repository: [bobes81/Petwell](https://github.com/bobes81/Petwell). Third-party packages and Bootstrap provide the framework/components identified above. Product descriptions, images and article content require owner review for accuracy, permission and attribution. This resubmission revision received AI-assisted code, testing and documentation changes; review and explain the code yourself and disclose assistance according to current Code Institute rules. No license or asset rights are assumed where none are recorded.
