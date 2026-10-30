# Final release handoff — 30 October 2026

Deadline: **31 October at 12:00 noon UK/Irish time (GMT)**. Preparation only: no merge, deployment, production connection/write, Render change, upload, account action or payment was performed. This supplements the [morning checklist](MORNING_HANDOFF.md) with the newly supplied service facts and a narrow local procedure; it does not repeat the Pass audit or test suite.

## Known configuration and exact-commit decision

The owner now reports the existing Render service as follows. These are owner-supplied facts, **not a dashboard inspection**:

| Setting | Reported actual value / repository finding |
| --- | --- |
| Connected branch / auto-deploy | `main` / enabled |
| Current production code | `6f0ac78` (repository main: `6f0ac78c2b772a22f5ee44a642da8927e0cc77c9`) |
| Build command | `./build.sh`; tracked script is executable. Both main's script and PR #8's script run migrations during build. |
| Start command | `gunicorn petwell.wsgi`. This is the existing setting, not proof of the explicit bind command suggested elsewhere. Do not change it merely to match documentation. |
| Reported environment names | `CLOUDINARY_URL`, `DATABASE_URL`, `DEBUG`, `SECRET_KEY`; private values and provider readiness remain unverified. |
| Reviewed application candidate | **`f75dbe1c6fb9c16f3895a5b01451e2de4d9b9160`** on PR #8, with [successful CI](https://github.com/bobes81/Petwell/actions/runs/41010383682). This documentation follow-up does not silently retarget a release to a later SHA. |

**A supported exact-commit mechanism exists; a safe end-to-end cutover on this service is not yet verified.** The official [Render CLI source, pinned at `cc851ae`](https://github.com/render-oss/cli/blob/cc851ae0da74a83067479b7ac91f9d30162c31b3/cmd/deploycreate.go) defines `render deploys create SERVICE_ID --commit COMMIT_ID --wait`; the [request adapter](https://github.com/render-oss/cli/blob/cc851ae0da74a83067479b7ac91f9d30162c31b3/pkg/tui/views/deploycreate.go) forwards the commit ID. This public source was read without installing/running/authenticating the CLI or calling a service API. It establishes the command's capability, not the installed version, account permissions, whether this service accepts an off-main SHA, or deployment while suspended. Render's [deploy documentation](https://render.com/docs/deploys) and [maintenance documentation](https://render.com/docs/maintenance-mode) could not be retrieved here (proxy HTTP 403); this is not a diagnosis of the owner's service.

The selected release mechanism, **only after all prerequisites below are independently verified and approved**, would be this command from an already installed/authenticated compatible CLI:

```bash
# WRITE / DEPLOY: DO NOT RUN during preparation or to test access.
# Set PETWELL_SERVICE_ID privately to the existing verified service, never a guess.
render deploys create "${PETWELL_SERVICE_ID:?}" \
  --commit f75dbe1c6fb9c16f3895a5b01451e2de4d9b9160 --wait
```

`--wait` starts a real deployment; it is not a dry-run. A dashboard exact-commit action is an alternative only if the owner verifies its actual supported behavior. Neither method itself prevents concurrent writes. **Do not execute either with the currently unverified writer-pause situation.** Do not merge into `main` or push there: auto-deploy is enabled and could start the migrating build. Do not change the connected branch/configuration as an access probe. Any future disabling of auto-deploy is a separately approved settings change; keep other main pushes/config-triggered builds out of the cutover window.

Before using that mechanism, the owner/operator must establish **all** of the following on the existing no-cost resources:

1. Permission and an independently supported route to deploy the exact SHA from this repository, without requiring a merge. Read-only dashboard/version/help inspection may identify the controls; the deploy command is not the verification probe. If off-main commit access cannot be confirmed, **STOP**.
2. An actual, verified way to stop/drain **every old database writer before the build**, maintain that boundary through migration and replace every old worker. Shell availability merely provides a command route; pre-deploy runs before the new workers and does not stop old ones; a maintenance page need not stop background jobs, existing requests or direct database writers. Suspension may also prevent deployment. No combination is assumed to work. **If no supported pause-and-deploy route can be established, this release is NO-GO and needs owner/Render support or a separately reviewed cutover design.**
3. Fresh recoverable backup at that pause boundary, verified target/server/tool versions and full migration history/schema, plus issued Stripe Session/delayed-event reconciliation. Keep the original 28 October backup. [Exact backup procedure and stop conditions](RELEASE_2026-10-30.md#approval-pause-and-fresh-backup). A checksum/index alone is not restore verification.
4. Explicit approval of the precise commit, pause/configuration/access/migration/deployment actions. Do not change the build command or move migrations now. Merely moving them into pre-deploy/startup does not establish a safe pause. The current build contains one migration stage; no duplicate manual production migration should be added casually.

Smallest read-only question for the owner to verify in the dashboard or with Render support: **“On our existing plan, what supported sequence stops and drains every old worker, permits deployment of an off-main exact commit whose build runs migrations, and prevents normal writes until that new revision is verified? Does suspension block deployment, and what controls cover background/direct writers?”** Do not send secrets or infer support from the mere presence of a Shell/maintenance button. No message was sent on the owner's behalf.

**Expected future cutover result:** exact approved SHA on all workers, six project migrations from the reported production baseline (`accounts.0001`, `orders.0002`–`0005`, `products.0002`), unchanged historical records/payment evidence, no pending migrations and successful deployment checks. Unexpected history/plan, old writers or health failure means stop; keep the pause and follow the [stage-specific recovery table](RELEASE_2026-10-30.md#if-anything-fails). A failed build may already have migrated the database. Do not perform a code-only rollback to `6f0ac78`, reverse migrations, fake records or blindly restore a backup over later writes.

## MacBook: rehearse only the availability migration

**Local disposable data only. Do not run these steps in Render Shell or with a production tunnel.** Prerequisites: existing local PostgreSQL 18 and client tools, the already-successful five-migration working database, this reviewed checkout with pinned requirements already installed, and no local app sessions using the source database during cloning. Retain the valuable source working database and original backup. This does not repeat the old five migrations or restore the 28 October backup again.

### 1. Make one new local disposable copy

Verify that the entered port is your actual local PostgreSQL server, not a proxy/tunnel. `petwell_availability_copy_20261030` is a **proposed new local database name**, not a known production/source name. Do not reuse it if it already exists. In a normal Mac terminal (zsh/bash):

```bash
(
  set -eu
  unset PGHOSTADDR PGSERVICE PGSERVICEFILE PGOPTIONS PGPASSWORD PGDATABASE
  printf 'Actual LOCAL PostgreSQL port: '; read -r LOCAL_PORT
  printf 'Actual LOCAL owner role: '; read -r LOCAL_ROLE
  printf 'Already-migrated LOCAL source database name: '; read -r LOCAL_SOURCE
  createdb --host=127.0.0.1 --port="${LOCAL_PORT:?}" \
    --username="${LOCAL_ROLE:?}" --password --maintenance-db=postgres \
    --template="${LOCAL_SOURCE:?}" petwell_availability_copy_20261030
)
```

Enter only the local database password at the private prompt. Expected: exit 0 and a newly copied local database; the source remains unchanged. **STOP** on missing tools, permission/version/connection errors, existing destination or active source sessions. Close only your known local applications and retry after review; do not kill unknown/production sessions, overwrite a database or buy a service.

### 2. Select the copy and check/apply exactly one migration

From the existing Petwell checkout, activate its existing virtualenv (`source venv/bin/activate`). `git status --short` must be clean; record `git rev-parse HEAD` and confirm it contains the reviewed candidate's unchanged application code. Do not reset/discard local work to obtain it. In this **local terminal only**:

```bash
unset DATABASE_URL SECRET_KEY CLOUDINARY_URL CLOUDINARY_CLOUD_NAME CLOUDINARY_API_KEY CLOUDINARY_API_SECRET STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET STRIPE_LIVE_MODE EMAIL_BACKEND SENDGRID_API_KEY PGHOSTADDR PGSERVICE PGSERVICEFILE PGOPTIONS PGPASSWORD
export REHEARSAL_DATABASE_URL="$(python -c 'from getpass import getpass; print(getpass("Private LOCAL COPY PostgreSQL URL: "))')"
export REHEARSAL_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
```

Enter the actual local-copy URL privately; percent-encode any special characters in its username/password. Required shape: `postgresql://LOCAL_ROLE:LOCAL_PASSWORD@127.0.0.1:LOCAL_PORT/petwell_availability_copy_20261030`, with actual credentials/port, **no query/fragment**, no production forwarding. Do not paste a real URL into Git/chat/history. The rehearsal profile disables Stripe, Cloudinary uploads and email, and has no production database fallback. It is not a network firewall.

Paste this block as a whole. It refuses a wrong copy name or any pending plan other than `products.0002`, takes private in-memory before/after fingerprints of every stored field in the five historical tables (excluding only the new availability column), applies that one local migration and prints only aggregate results:

```bash
python - <<'PY'
import hashlib
import json
import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'petwell.rehearsal_settings'
django.setup()
from django.core.management import call_command
from django.db import connection, transaction
from django.db.migrations.executor import MigrationExecutor

def require(condition, message):
    if not condition:
        raise SystemExit('STOP: ' + message)

require(connection.vendor == 'postgresql', 'PostgreSQL required.')
require(connection.settings_dict['NAME'] == 'petwell_availability_copy_20261030',
        'The target must be the newly created disposable local copy.')
executor = MigrationExecutor(connection)
plan = [(m.app_label, m.name, backwards) for m, backwards in
        executor.migration_plan(executor.loader.graph.leaf_nodes())]
print('Pending plan:', plan)
require(plan == [('products', '0002_product_is_available', False)],
        'Expected only products.0002. Already applied or other pending work: review; never downgrade/fake.')

tables = ('products_product', 'orders_order', 'orders_orderitem',
          'blog_blogpost', 'blog_subscriber')

def snapshot():
    result = {}
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute('SET TRANSACTION READ ONLY')
        for table in tables:
            cursor.execute('SELECT * FROM ' + connection.ops.quote_name(table) + ' ORDER BY id')
            columns = [c[0] for c in cursor.description]
            rows = [{key: value for key, value in zip(columns, row)
                     if key != 'is_available'} for row in cursor.fetchall()]
            digest = hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()
            result[table] = (len(rows), digest)
    return result

with connection.cursor() as cursor:
    cursor.execute('SHOW server_version')
    print('Local server version:', cursor.fetchone()[0])
    cursor.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=current_schema() AND table_name='products_product' AND column_name='is_available'")
    require(cursor.fetchone()[0] == 0, 'Unexpected availability column before migration.')
before = snapshot()
require(before['products_product'][0] > 0, 'Empty copy is not the restored-data rehearsal.')
call_command('migrate', 'products', '0002_product_is_available', interactive=False)
require(snapshot() == before, 'Historical field/count fingerprint changed; keep the copy for investigation.')
executor = MigrationExecutor(connection)
require(not executor.migration_plan(executor.loader.graph.leaf_nodes()), 'Pending migrations remain.')
with connection.cursor() as cursor:
    cursor.execute('SELECT count(*) FROM products_product WHERE is_available IS DISTINCT FROM TRUE')
    require(cursor.fetchone()[0] == 0, 'Existing products must default to available, including PDF.')
print('PASS: only products.0002 applied; all historical fields/counts preserved; all availability flags true; no pending migrations.')
print('Preserved counts:', {table: value[0] for table, value in before.items()})
connection.close()
PY
```

Expected migration: `products.0002_product_is_available... OK`, followed by the PASS summary. Original snapshot counts were 10 products / 5 orders / 5 items / 2 posts / 2 subscribers; documented local browser additions may increase them. Require before/after equality, not blind equality to those old totals. No PDF is withdrawn. **Any error or STOP means do not release; do not rerun the migration backwards or reset the copy.** Keep a private dated result with actual checkout SHA/server version; share only a sanitised summary. This block is prepared, not executed here against the owner's copy.

### 3. Read-only PDF and image review

On that migrated local copy, this command is read-only (no `--apply`):

```bash
python manage.py review_legacy_pdf --settings=petwell.rehearsal_settings
```

Expected: `DRY_RUN`, exact-name candidates and aggregate history/fingerprint, no modified availability. Privately verify the actual description/image and outstanding obligations with the owner; no/duplicate/uncertain matches mean stop identification. Local IDs and fingerprints must be reverified on the intended production database **only after separate access approval and the correct schema**; they are not production authority. The [existing exact-row procedure](LEGACY_PDF_WITHDRAWAL.md) covers future approved application and Session reconciliation, not an action now.

For the nine supplied source files, this separate check is source-only and performs no SQL/provider operations:

```bash
python manage.py associate_product_images docs/catalogue/catalogue-images.DRAFT.json \
  --images-dir docs/catalogue/concepts --sources-only \
  --settings=petwell.rehearsal_settings
```

Expected: nine validated sources; rights and operational metadata still pending. This does not verify actual Cloudinary delivery or record association. Review the [nine originals/inventory](catalogue/README.md) privately for accuracy/rights. Do not run normal association against the incomplete draft, guess IDs/public IDs/versions, use `--apply`, clear existing fields or upload. The rehearsal intentionally has no cloud configuration; complete Cloudinary/record dry-run needs a separately authorised profile/target as described in [the existing workflow](CATALOGUE_IMAGES.md). At the end, `unset REHEARSAL_DATABASE_URL REHEARSAL_SECRET_KEY`; retain the valuable baseline/backup.

## Release decision — minimal owner gates

| Gate | GO requires | NO-GO / owner action still needed |
| --- | --- | --- |
| Exact code and safe cutover | Approved SHA with its green CI, verified off-main deployment support, auto-deploy contention controlled with approval, all old writers drained before migrating build | **Not verified on the actual service.** Owner must inspect existing controls/support; no Shell/maintenance/pre-deploy assumption is accepted. Do not deploy to discover the answer. |
| Local migration / fresh recovery | Above one-migration rehearsal passes; fresh paused-boundary backup can actually restore with compatible tools and preserves later-write accounting | Owner's earlier five-migration rehearsal is completed. Only the new local step and release-time backup/target/history checks remain; never rerun all five unnecessarily. |
| Offer and images | Correct PDF reviewed/withdrawn under separate approval after migration; history/obligations preserved; nine authorised accurate illustrations associated using real metadata and existing images preserved | Read-only preparation is available. Actual product identity, fulfilment/rights and approved data/upload operations remain private owner actions. |
| Stripe sandbox | Same-account test API key and exact deployed `/checkout/webhook/` secret, live mode false; approved real site-created test Session, signed matching success, cart/replay and decline/cancel/retry evidence | Existing four variables do not configure Stripe. No account was accessed and no transaction was initiated. A sample event, mocked test or return page is not acceptance. |
| Cloudinary | Existing `CLOUDINARY_URL` works for authorised upload/replace/clear and HTTPS rendering; correct nine associations and disclosures verified | Offline sources/URL handling do not prove upload rights/quota/delivery. Separate approval and genuine owner/provider results required; no paid resource. |
| SMTP and deployed UX | Existing Gmail/alternative credentials and SMTP egress work; controlled mailbox actually receives a valid HTTPS reset link; private CRUD/history/SEO/static/persistence checks pass on approved revision | Settings remain environment-only. Console/dummy email and local screenshots are not deployed acceptance. [Detailed configuration/acceptance](RENDER_CHECKLIST.md). |

**Current result: NO-GO for executing production cutover, reopening checkout or claiming completed external acceptance.** The unresolved writer-pause/deploy compatibility is the first technical release blocker; private access/approval and genuine provider acceptance cannot be completed through repository documentation. On **iPad**, inspect/approve the precise future actions and review supplied originals/configuration names; do not press Deploy/Save or expose secrets. On **MacBook**, perform the isolated copy/rehearsal and private backup/tool checks. Only after those gates can the owner authorise a production window and separately authorised sandbox/image/email acceptance. Use the [Pass matrix](PASS_COMPLIANCE_MATRIX.md) and the owner's actual issued guide for submission; no Pass is guaranteed.

Preparation validation: 343 internal documentation links/Markdown anchors resolve; all six shell blocks pass `bash -n`, and the embedded Python passes `ast.parse`. These are syntax/static checks only: the proposed clone, migration and deployment blocks were **not executed**, and their owner/service prerequisites remain mandatory. No application code or workflow changed and no Django tests were rerun.
