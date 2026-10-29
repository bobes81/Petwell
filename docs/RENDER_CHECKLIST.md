# Render configuration and release checklist

The owner reported these existing Render environment-variable **names** on 28 October 2026: `CLOUDINARY_URL`, `DATABASE_URL`, `DEBUG` and `SECRET_KEY`. Their secret values, current deployed revision and external-service operation were not inspected. This review changes repository code and documentation only; it does not modify Render, deploy, merge, create resources or enable live payments.

## Backup restoration reported on 29 October

The owner reports successfully restoring the **28 October Render PostgreSQL backup** into an isolated **PostgreSQL 18 database on their MacBook**, containing **10 products, 5 orders and 2 blog posts**. This is useful owner-performed restore evidence; no dump, connection string, customer record or screenshot is published here. The repository review did not connect to that database or independently repeat the restore.

The selected counts confirm reported restored content, not completion of the pending migrations, all-table/relationship checks, safe code cutover, production-version compatibility or external acceptance. Preserve the restored baseline and rehearse the upgrade on a separate local working copy using the [local-only rehearsal instructions](RESTORED_DB_REHEARSAL.md). Do not repeat the completed restore merely to satisfy this checklist. Record the private backup/restore reference, selected revision and genuine before/after results; the [runbook](RELEASE_RUNBOOK.md) separates that rehearsal from an approved production recovery.

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

Unmapped attempts with a saved payload are automatically retried only while younger than 23 hours. At that boundary the app preserves the pending order/cart/payload and requests review, including after changed customer/cart data. Stripe's [idempotency documentation](https://docs.stripe.com/api/idempotent_requests) describes key pruning after at least 24 hours; the guard leaves a margin rather than assuming permanent deduplication. Known Session IDs can still be retrieved. Reconcile a held attempt under approved provider access before any replacement; a browser return or an empty local mapping is not proof of payment outcome.

## SMTP — delivery is not enabled by the four reported variables

Email defaults to the console backend, which writes messages to the process log and does not deliver them. Do not publish logs containing password-reset links. The current supported SMTP setup is SendGrid:

- `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- private `SENDGRID_API_KEY`
- `DEFAULT_FROM_EMAIL` using an actually verified sender

Settings use `smtp.sendgrid.net`, port 587, STARTTLS, username `apikey` and a 10-second timeout. `EMAIL_HOST_PASSWORD` is not a process-environment alias in this project; the password comes from `SENDGRID_API_KEY`. No provider account, subscription or paid resource was created or changed. Do not claim delivery until an actual reset email is received and its link works against the correct deployed hostname. Local in-memory email/token tests are separate evidence.

Order payment state does not depend on SMTP. Automatic order-confirmation email dispatch is not implemented; a newsletter record is not campaign-delivery evidence.

## Migrations and release — owner-controlled actions

The owner confirms applied `orders.0001_initial`, `products.0001_initial` and `blog.0001` through `blog.0004_merge_20260213_0814`, including both conflicting branches and the merge. Those migration files are unchanged relative to `main` (`6f0ac78`); no applied migration was rewritten. The owner also confirms `orders.0002`–`0005` and `accounts.0001_initial` are not yet applied. This confirmation updates the previously partial project-app history; it is not an inspection of production data or a claim that new features are deployed. Authentication, allauth, sites, sessions and admin history/schema must also agree before release. If a table exists without matching migration records, stop and review that discrepancy; do not guess, delete records or automatically use `--fake`/`--fake-initial`.

| Project migration path | Forward effect from the reported baseline |
| --- | --- |
| `products.0001_initial` | Already reported applied; no new products migration or image-data rewrite. |
| `orders.0001_initial` → `0002_order_paid_at_order_public_id_order_status_and_more` | Adds public UUID, pending status, optional Stripe Session and paid timestamp. Each existing order gets a distinct UUID and remains unpaid; original order/item data is preserved. |
| `orders.0003_alter_orderitem_product` | Protects products referenced by order items from ORM deletion. |
| `orders.0004_order_cart_line_tokens_order_stripe_checkout_payload` | Adds empty per-order JSON snapshots; does not invent payment evidence or clear legacy carts. |
| `orders.0005_checkoutstate` | Creates the durable checkout coordinator; its active-order reference is protected. |
| `accounts.0001_initial` | Creates owner-linked PetProfile; this app is distinct from allauth's `account` app. |
| `blog.0001_initial` → both `0002` branches → `0003` → `0004_merge_20260213_0814` | Confirmed applied. Initial migration creates BlogPost and Subscriber. The subsequent historical branches and merge contain no operations; their filenames do not imply a second Subscriber table. The upgrade must not replay these migrations or alter existing blog/subscriber data. |

The isolated regression reconstructs the confirmed order/product/blog baseline and its required auth/contenttypes dependencies. It inserts synthetic member/guest orders, items, a product/image reference, an existing blog post/image and a subscriber. It verifies that the project-app forward plan contains exactly the four pending orders migrations and one accounts migration, with no product/blog replay. After upgrading every current leaf it checks preserved IDs, relationships, content, contact data, timestamps and historical amounts, unique pending-order UUIDs, empty payment snapshots, usable new tables, protected deletions and no remaining plan. The same regression runs on SQLite locally and the disposable PostgreSQL CI service. Other apps are included through their minimum dependency closure, not inferred to have that exact state in production. The fixture cannot detect unknown production drift, lock duration or data-volume problems.

1. Review the PR and selected commit, keep automatic deployment disabled during review, and explicitly approve deployment before proceeding.
2. Verify the existing PostgreSQL target privately and take a recoverable backup. Inspect `python manage.py showmigrations` and `python manage.py migrate --plan` under the approved production settings without copying connection details to evidence.
3. Coordinate an approved maintenance/write-pause window before schema cutover. The new required order fields have application defaults; an old `orders.0001` worker cannot insert an order after the upgrade. The isolated regression confirms that old-model insert fails. `build.sh` applies migrations while an old web process may still be serving, so a successful build alone does not establish a safe cutover. Review how the existing service will stop old writes and switch to the new revision; no zero-downtime guarantee is claimed.
4. Apply all outstanding migrations with `python manage.py migrate --noinput`. Required project migrations include `accounts.0001_initial` and `orders.0002` through `orders.0005_checkoutstate`. Historical orders without Stripe proof stay pending. Do not fake, skip, edit already applied migrations or manually mark old orders paid.
5. `bash build.sh` installs requirements, collects static files and runs migrations. If the existing Render plan supports a pre-deploy command, run migrations there and use dependency installation/static collection as the build command; this still requires the write-pause/cutover review above. No plan upgrade or new resource is required by this document. Back up first in either case. Start with `gunicorn petwell.wsgi:application --bind 0.0.0.0:$PORT`.
6. Run `python manage.py check --deploy --fail-level WARNING` using the approved configuration. Verify HTTPS, secure cookies, static files and the correct crawler domain after release. A passing Django check does not prove external credentials or persistence work.
7. Complete the actual Stripe, Cloudinary image upload/replace/clear, received-reset-email and persistent-database checks. Repeat owner-only pet CRUD, blog permissions and order privacy on the deployed revision. Capture genuine dated evidence with secrets and personal data excluded.

No additional schema migration is introduced by this readiness review. Do not blindly downgrade `orders` or roll back to old code after applying the new schema: reverse migrations remove payment fields/snapshots and the coordinator table. Choose a reviewed forward fix or an explicitly approved restoration that preserves and reconciles post-backup writes and external Stripe state; use the [release/recovery decision table](RELEASE_RUNBOOK.md). Reversing migrations inside the disposable regression database is test setup only, never a production recovery instruction.

## Release decision — NO-GO until the outstanding gates are verified

The current recommendation is **NO-GO for a production release or a claim that end-to-end payment acceptance is complete**. Repository tests and isolated migration rehearsals cannot establish the state of an existing deployment. No production database, private configuration, Stripe destination or Render service was accessed during this review.

| Gate | Evidence required before release | Current boundary |
| --- | --- | --- |
| Submitted revision | Current PR head, successful SQLite/PostgreSQL CI and actual local test output | Use the final reviewed commit's results; an earlier green run does not establish a later commit's status. |
| Backup restore rehearsal | Private backup/restore reference and actual target/version/content checks | Owner reports a successful isolated PostgreSQL 18 restore of the 28 October backup with 10 products, 5 orders and 2 blog posts. This advances the restore gate; all-table integrity, post-backup write accounting and suitability of the release-time backup still need verification. |
| Complete migration state and cutover | Full migration/schema agreement, reviewed forward/recovery plan and prevention of old-code order writes during cutover | Owner confirms order/product initial migrations and complete blog history; `orders.0002`–`0005` and `accounts.0001` remain pending. Upgrade of a working copy of the restored data, other installed-app/schema checks and service cutover are not yet reported complete. The synthetic regression preserves existing blog/commerce data; old-model order writes fail after it. |
| Production configuration | Correct existing database, strong existing secret, DEBUG off, HTTPS host and valid Cloudinary account/upload access | Variable-name compatibility is tested; private values and external access are not verified. |
| Stripe sandbox | Same-account test API key and exact endpoint signing secret, live mode off, actual signed delivery and success/decline/cancel/retry acceptance | The route and offline signature/state logic are tested. The four reported variables alone do not configure Stripe, and no real sandbox checkout/delivery is claimed. |
| Customer email | Configured SMTP backend, authorised sender and actually received password-reset email | Local token/email tests pass separately; console output is not delivery. Payment state remains independent of SMTP. |
| Offered catalogue | Accurate authorised product photos/source records and a fulfilment process matching every offer | Existing placeholder images do not meet genuine-photo requirements. The seeded PDF listing must have verified fulfilment or be removed from the offered catalogue. |
| Release approval | Owner review and explicit approval of the exact commit and release actions | This review does not merge, deploy, change Render or authorise live payments. |

Do not run `bash build.sh` against a production `DATABASE_URL` as a read-only readiness check: it applies migrations and writes to the database during the build, before the web process starts. The backup and explicit release approval gates must precede that operation. Reuse existing resources; no paid resource or plan change is required by this checklist.

After the owner verifies the outstanding gates and explicitly approves a release, record the selected commit, migration outcome and genuine deployed acceptance evidence. Until then, retain this NO-GO decision and the pending statuses rather than treating local or mocked tests as external verification.

Latest local evidence: [complete suite](evidence/28oct-confirmed-history-tests.txt), [confirmed-blog migration rehearsal](evidence/28oct-confirmed-blog-migration-tests.txt), [two new signed-webhook regressions](evidence/28oct-sandbox-webhook-followup-tests.txt) and [system/migration/deployment/dependency checks](evidence/28oct-confirmed-history-checks.txt). These files contain synthetic/local results, not production observations. Earlier evidence remains preserved.

See [README](../README.md) for installation/environment details, [TESTING](TESTING.md) for actual results, [EVIDENCE](EVIDENCE.md) for submission gaps and [ASSETS](ASSETS.md) for accurate product-photo/source requirements.
