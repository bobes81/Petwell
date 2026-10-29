# Isolated restored-database rehearsal on the owner's Mac

On **29 October 2026**, the owner reported successfully restoring the **28 October Render backup** into an isolated **PostgreSQL 18** database on their MacBook: **10 products, 5 orders and 2 blog posts**. This is owner-reported restore evidence. This repository review did not access the database or independently verify those counts, all records, migration outcome, browser behaviour or external services.

The next step is a rehearsal on a **disposable local working copy**, keeping the original backup and first restored database untouched. It is separate from any approved production release. Do not upload/commit the dump, database credentials or customer data. A successful restore into version 18 does not establish that a new version 18 dump can be restored into an older production server; retain the original Render backup and verify the actual recovery target/version before any later restore.

## Local-only configuration

`petwell.rehearsal_settings` requires an explicit `REHEARSAL_DATABASE_URL` for a named PostgreSQL database on `localhost`, `127.0.0.1` or `[::1]`. It rejects remote hosts, maintenance databases, URL query/fragment options and libpq service/host-address overrides. It never falls back to `DATABASE_URL`. A loopback address does not prove that a port is not a tunnel: verify the selected server/port belongs to the disposable local copy, with no proxy/forward to production.

This profile permits local PostgreSQL without forcing SSL; ordinary `petwell.settings` still requires database SSL for Render. It uses normal password hashing/validators, a separate local Django secret, local HTTP, DEBUG off and loopback allowed hosts. Stripe keys are blank/live mode false, Cloudinary credentials are cleared (images use placeholders), and the dummy email backend neither sends nor prints messages. Upload/payment/email acceptance is deliberately unavailable in this rehearsal. This configuration is not a network firewall and must never serve Render or a public interface.

Do **not** use `petwell.test_settings` or `petwell.postgres_test_settings` to run the restored application. Do not run the Django test runner, `flush`, production seed, `build.sh`, fake migrations or schema downgrades against the valuable restored database. Automated tests use disposable test databases; the owner rehearsal uses an explicitly selected working copy.

## Working-copy steps — to be performed by the owner locally

1. Keep the original 28 October backup private and intact. Make a separate disposable working database using the owner's already verified local restore method. Review the selected checkout/commit and isolate the terminal from production credentials; keep only the local role/password needed for that working copy. Do not create a paid service or alter Render configuration.
2. Activate the project virtualenv and install the pinned requirements if not already installed. In a **local rehearsal terminal only**, clear stale production/service bindings before startup; base settings still parse inherited values before the profile overrides them. Do not run this command in a production shell:

   ```bash
   unset DATABASE_URL SECRET_KEY CLOUDINARY_URL CLOUDINARY_CLOUD_NAME CLOUDINARY_API_KEY CLOUDINARY_API_SECRET STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET STRIPE_LIVE_MODE EMAIL_BACKEND SENDGRID_API_KEY PGHOSTADDR PGSERVICE PGSERVICEFILE PGOPTIONS
   ```

   Set `REHEARSAL_DATABASE_URL` privately in that local shell/IDE, using the actual local copy's role, port and name. Standard shape: `postgresql://<local-user>:<local-password>@127.0.0.1:5432/<working-copy>`, without query/fragment options. Do not paste the actual value into chat, public logs or this document. Generate a separate process-only secret without printing it:

   ```bash
   export REHEARSAL_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
   ```

3. Inspect the working copy's migration history/plan. These commands read that local copy; they do not apply migrations:

   ```bash
   python manage.py check --settings=petwell.rehearsal_settings
   python manage.py showmigrations --settings=petwell.rehearsal_settings
   python manage.py migrate --plan --settings=petwell.rehearsal_settings
   ```

   Compare with the confirmed project baseline: `orders.0001`, `products.0001`, complete blog through `0004` including both branches/merge; project migrations pending are `orders.0002`–`0005` and `accounts.0001`. Other installed-app history must agree too. Stop if the target, records or tables differ; do not repair a mismatch by guessing or automatically faking migrations.
4. Record private before-migration counts and selected non-sensitive integrity checks on the **working copy**. The reported 10/5/2 describes the original restored snapshot, not a fresh production count. A shell count uses no new order fields and can run before the upgrade:

   ```bash
   python manage.py shell --settings=petwell.rehearsal_settings -c 'from products.models import Product; from orders.models import Order, OrderItem; from blog.models import BlogPost, Subscriber; print({"products": Product.objects.count(), "orders": Order.objects.count(), "order_items": OrderItem.objects.count(), "posts": BlogPost.objects.count(), "subscribers": Subscriber.objects.count()})'
   ```

5. Only after verifying it is the disposable local copy, apply the forward migrations there:

   ```bash
   python manage.py migrate --noinput --settings=petwell.rehearsal_settings
   python manage.py migrate --check --settings=petwell.rehearsal_settings
   ```

   Repeat the same counts **before** adding browser-test records. Verify original order/item primary and foreign keys, quantities, historical amounts, product/article image references, blog/subscriber content and timestamps. Old orders must have distinct UUIDs, pending status, no paid timestamp/Stripe evidence and empty snapshots. The migration should preserve existing row counts; counts alone are not a full integrity check. Keep any record-level/customer comparison private.
6. For browser checks, collect local static files and bind only to loopback:

   ```bash
   python manage.py collectstatic --noinput --settings=petwell.rehearsal_settings
   python manage.py runserver 127.0.0.1:8000 --settings=petwell.rehearsal_settings
   ```

   Use new synthetic local accounts/records for pet/blog CRUD and permissions, order display and cart validation. Account creation/edits change only the disposable copy. Checkout must remain unavailable and preserve the cart; no paid status or provider call should be fabricated. Existing image placeholders and absent email delivery are expected with this profile. Do not publish real customer/order information in screenshots; browser success here is local evidence, not Render/Stripe/Cloudinary/SMTP acceptance.
7. Record the actual local date, commit, PostgreSQL version, migration labels, before/after comparisons and browser outcomes. Leave unperformed checks pending. Preserve the initial restored copy; stop the local server when finished. Share only a sanitised summary, not the dump or connection string.

## Release gate after rehearsal

Even a successful local migration rehearsal does not authorise deployment. Production needs an approved exact-commit cutover/write pause, a fresh backup accounting for writes since 28 October, full schema/configuration checks, actual sandbox/webhook and image/email acceptance, and the remaining catalogue/assessment evidence. Follow [RENDER_CHECKLIST.md](RENDER_CHECKLIST.md) and [RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md). No live payment or production operation is part of this local procedure.
