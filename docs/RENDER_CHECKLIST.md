# Render configuration and release checklist

The owner reported these existing Render environment-variable **names** on 28 October 2026: `CLOUDINARY_URL`, `DATABASE_URL`, `DEBUG` and `SECRET_KEY`. Their secret values, current deployed revision and external-service operation were not inspected. This review changes repository code and documentation only; it does not modify Render, deploy, merge, create resources or enable live payments.

## Existing configuration compatibility

| Variable | Expected configuration | Review boundary |
| --- | --- | --- |
| `CLOUDINARY_URL` | Existing private `cloudinary://<api-key>:<api-secret>@<cloud-name>` credential URL, loaded through the Cloudinary SDK. Generated image URLs use HTTPS. | No separate Cloudinary variables are required when this URL is supplied. Use one credential source: the SDK gives separate variables precedence when `CLOUDINARY_CLOUD_NAME` is set, otherwise it loads the URL. Parsing/rendering can be tested offline; actual account credentials, assets and upload permission still need owner verification. Never print or screenshot the full URL. |
| `DATABASE_URL` | Persistent PostgreSQL connection URL for the existing database; production settings require SSL. | Do not replace it with a local/test database or assume its contents were verified here. Back up before migrations. |
| `DEBUG` | `False` for production. | Do not expose a Django debug page containing configuration or request data. |
| `SECRET_KEY` | Existing strong private Django secret. | Its value was not inspected or changed. Do not rotate it solely for this patch. |

The deployed hostname defaults to `petwell-u0cr.onrender.com` and `SITE_URL` defaults to `https://petwell-u0cr.onrender.com`. Explicit `ALLOWED_HOSTS` and `SITE_URL` overrides are optional for that exact target; a real custom domain requires matching trusted values. Use `petwell.settings`, never test settings, for the application.

## Stripe sandbox — additional configuration required

The four reported variables do not configure payment processing. Checkout remains unavailable and preserves the cart until both `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` are configured privately. Assessment must use the same Stripe sandbox/test account for the API key and webhook destination, with `STRIPE_LIVE_MODE=False` (the default). Live keys are rejected in this mode. Hosted Checkout does not need a publishable key.

For an approved deployment, use the sandbox destination `https://petwell-u0cr.onrender.com/checkout/webhook/` with `checkout.session.completed` and `checkout.session.async_payment_succeeded`. A CLI listener has its own signing secret; it cannot substitute for the deployed endpoint's secret. Never copy either secret into Git, chat or evidence.

Offline tests verify key/mode guards, signed fixture validation, exact order/Session/amount/currency/mode matching and idempotent pending-to-paid handling. They do not verify real Stripe API access or webhook delivery. After deployment approval, record a genuine sandbox success, decline/cancellation, retry and duplicate delivery. Confirm that the return URL alone cannot mark paid and that cart reconciliation follows webhook confirmation. Do not use a real card or turn on live mode.

## SMTP — delivery is not enabled by the four reported variables

Email defaults to the console backend, which writes messages to the process log and does not deliver them. Do not publish logs containing password-reset links. The current supported SMTP setup is SendGrid:

- `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- private `SENDGRID_API_KEY`
- `DEFAULT_FROM_EMAIL` using an actually verified sender

Settings use `smtp.sendgrid.net`, port 587, STARTTLS, username `apikey` and a 10-second timeout. `EMAIL_HOST_PASSWORD` is not a process-environment alias in this project; the password comes from `SENDGRID_API_KEY`. No provider account, subscription or paid resource was created or changed. Do not claim delivery until an actual reset email is received and its link works against the correct deployed hostname. Local in-memory email/token tests are separate evidence.

Order payment state does not depend on SMTP. Automatic order-confirmation email dispatch is not implemented; a newsletter record is not campaign-delivery evidence.

## Migrations and release — owner-controlled actions

1. Review the PR and selected commit, keep automatic deployment disabled during review, and explicitly approve deployment before proceeding.
2. Verify the existing PostgreSQL target privately and take a recoverable backup. Inspect `python manage.py showmigrations` and `python manage.py migrate --plan` under the approved production settings without copying connection details to evidence.
3. Apply all outstanding migrations with `python manage.py migrate --noinput`. Required project migrations include `accounts.0001_initial` (PetProfile) and `orders.0002` through `orders.0005_checkoutstate` (payment identity/state, protected items, immutable checkout/cart snapshots and checkout coordinator). Historical orders without Stripe proof stay pending. Do not fake, skip, edit already applied migrations or manually mark old orders paid.
4. `bash build.sh` installs requirements, collects static files and runs migrations. If the existing Render plan supports a pre-deploy command, run migrations there and use dependency installation/static collection as the build command; no plan upgrade or new resource is required by this document. Back up first in either case. Start with `gunicorn petwell.wsgi:application --bind 0.0.0.0:$PORT`.
5. Run `python manage.py check --deploy --fail-level WARNING` using the approved configuration. Verify HTTPS, secure cookies, static files and the correct crawler domain after release. A passing Django check does not prove external credentials or persistence work.
6. Complete the actual Stripe, Cloudinary image upload/replace/clear, received-reset-email and persistent-database checks. Repeat owner-only pet CRUD, blog permissions and order privacy on the deployed revision. Capture genuine dated evidence with secrets and personal data excluded.

This configuration change does not require a new schema migration. Fresh-database and legacy-order migration regressions are covered by the isolated Django suite; the actual production database's applied state remains unverified.

See [README](../README.md) for installation/environment details, [TESTING](TESTING.md) for actual results, [EVIDENCE](EVIDENCE.md) for submission gaps and [ASSETS](ASSETS.md) for accurate product-photo/source requirements.
