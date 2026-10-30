# Owner handoff — deployed with Maintenance Mode enabled

Updated **30 October 2026**. Deadline: **31 October, 12:00 noon UK/Irish time (GMT)**. Owner verified production commit **`f75dbe1c6fb9c16f3895a5b01451e2de4d9b9160`**, successful build and all six migrations. The service is running in Render; **Maintenance Mode remains enabled**. [Verification boundaries and evidence](evidence/30oct-production-deployment.md).

## Completed — do not repeat by default

- Production build/deployment/six migrations: owner verified. Later documentation commits are not claimed as deployed.
- Actual uploaded-backup PostgreSQL 18.6 rehearsal: six migrations, original records/fields preserved, no pending migrations; [sanitised result](evidence/30oct-real-backup-migration-rehearsal.json).
- Deployed-baseline CI: SQLite **189 passed + one PostgreSQL-only skip**; PostgreSQL **190 passed**, with SQLite/PostgreSQL 16/18 [green CI](https://github.com/bobes81/Petwell/actions/runs/41010383682).
- Genuine local browser/design/validator evidence remains in [TESTING.md](TESTING.md). No live browser/provider acceptance is inferred.

## Smallest remaining owner actions

| Priority | Action | Device |
| --- | --- | --- |
| 1 | Verify actual PDF/physical fulfilment, nine image accuracy/rights and private service configuration. The image manifest is a draft, not proof of production assignment. | **iPad:** review/dashboard/files. **MacBook:** documented private manifest/guarded commands when separately approved. |
| 2 | Arrange separately approved deployed acceptance: sandbox Checkout and matching webhook/replay/cart/failure checks, real Cloudinary rendering/upload and received reset email; auth/private CRUD/history/mobile/SEO. Keep genuine redacted evidence. | **iPad:** browser/email/dashboard checks. **MacBook:** desktop/keyboard and any required approved CLI. No paid tool or real/live payment. |
| 3 | Owner decides reopening/maintenance changes only after the relevant checks; update actual results and submit correct links with issued-guide/assistance review. | **Either device.** This document does not disable maintenance or authorise new production/provider actions. |

[Ordered acceptance checklist](OWNER_RELEASE_CHECKLIST.md), [Pass evidence matrix](PASS_COMPLIANCE_MATRIX.md), [configuration](RENDER_CHECKLIST.md). The earlier [deployment handoff](FINAL_RELEASE_HANDOFF.md) and [30 October cutover plan](RELEASE_2026-10-30.md) remain dated references; their pre-deployment blockers are not a request to redo completed work. Any future deploy still needs its own reviewed safe cutover/backup.

Current **NO-GO** concerns opening the storefront or claiming completed external/end-to-end acceptance, not the completed deployment. No Pass is guaranteed. The full official guide remains unavailable in the checkout; no raw customer data, secret values, private feedback or invented screenshots/results should be published.
