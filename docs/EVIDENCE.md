# Genuine submission evidence checklist

This checklist separates evidence already captured locally from checks still required on an approved deployment. Local results are not proof of external integration or production readiness. Do not fabricate reports, diagrams, screenshots, social metrics or test outcomes. Identify any remaining limitation honestly before submission.

| Evidence | What to supply | Status |
| --- | --- | --- |
| Assessor feedback and rubric mapping | Map each returned assessment issue to code, test and evidence | Private summary supplied 28 Oct; project evidence mapped in ASSESSMENT_REVIEW.md; official guide/sign-off still unverified |
| Wireframes | Original planning files or clearly labelled retrospective diagrams | New dated HTML wireframes/local renders in docs/design; historical original planning not claimed |
| Schema diagram | [Implemented model diagram](MODELS.md), reflecting this revision rather than historical planning | Added; review against assessment rubric |
| Responsive screenshots | Deployed pages at phone/tablet/desktop widths, real navigation expanded/collapsed, no overflow | Local Chromium checks at desktop 1440×1000 and mobile 390×844: 10 grouped flows and 16 genuine screenshots linked in [TESTING.md](TESTING.md). Tablet, other browsers and deployed checks remain pending. |
| Stripe test checkout | Sandbox hosted page and confirmed in-app order; redact credentials, personal details and payment identifiers as needed | TODO after authorised deployment |
| Webhook evidence | Test event delivery with HTTP 200 and matching paid order; duplicate delivery not duplicating an order | TODO |
| Blog permissions and CRUD | Own post create/edit/delete, image retention/validation, non-owner direct URL denial, staff moderation | Automated regressions and local browser CRUD/validation/permission checks recorded in [TESTING.md](TESTING.md); real Cloudinary and deployed checks remain pending. |
| My pets | Owner-only profile create/read/update/delete, validation, focus reminder, direct-URL denial to other members/staff | Automated and local browser checks recorded in [TESTING.md](TESTING.md); deployed verification remains pending. |
| My orders / Buy again | Two users, isolated histories, paid reorder using a changed current price | Automated and local browser checks passed using explicitly labelled synthetic paid-order fixtures. This is not real payment evidence; see [browser results](evidence/28oct-browser-results.json). |
| Automated tests | Save actual command, date, test count and output for the submitted revision | Latest local SQLite record including configuration and strengthened migration regressions: 114 tests, 113 passed, 1 PostgreSQL-only skip, 0 failures; [actual output](evidence/28oct-deployment-readiness-tests.txt). Confirm the final submitted head and its SQLite/PostgreSQL CI results. |
| Migration/release readiness | Verify the complete applied history/schema, backup/recovery and code/schema cutover | Reported `orders.0001`/`products.0001` fixture upgrade is tested; production was not accessed. Full owner verification and release approval remain pending: [NO-GO gates](RENDER_CHECKLIST.md). |
| Accessibility and validators | Recorded markup, keyboard, contrast, zoom and browser findings, with dates and scope | Local Nu HTML/CSS checks passed for 19 HTML documents and 2 project CSS files. The separate strict style audit failed and is disclosed in [TESTING.md](TESTING.md). Full accessibility, Lighthouse and deployed validation remain pending. |
| Facebook page or clearly labelled mockup | Distinguish published-page evidence from a design proposal | New HTML mockup and local renders in docs/marketing; no live page claimed |
| Marketing evidence | Actual dated posts/strategy; only report reach/engagement where measured | TODO |
| Image/source credits | Verify each used asset's source and permission, including legacy assets | Actual legacy-file observations and catalogue-photo readiness checklist are in [ASSETS.md](ASSETS.md). Accurate authorised catalogue photos and source/permission records remain missing. |

Retain genuine files under `docs/evidence/` and link them from README/TESTING with captions, dates and local/deployed scope. Do not include customer data, account tokens, keys, dashboard signing secrets or card information. The old `static/images/ facebook-mockup-petwell.png` is only a watermarked title card, not Facebook UI. The new design proposal is in `docs/marketing/` and is explicitly not published. See [ASSETS.md](ASSETS.md).

Suggested order before the 31 October 2026, 12:00 UK deadline: review assessor feedback → review code/tests → configure test integrations → explicitly approve deployment → run deployed acceptance checks → capture evidence → check README links and final submitted commit.
