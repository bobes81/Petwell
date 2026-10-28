# Resubmission evidence map — 28 October 2026

The owner supplied a private summary of failed criteria during this review. The correspondence and pasted summary are **not included in this repository**. This document describes the project's work in our own words. No official assessment guide was available in the checkout, so the identifiers below are traceability references, not invented official criterion descriptions or assessor sign-off. The resubmission is capped at Pass; no Pass is guaranteed.

Deadline: **31 October 2026, 12:00 noon Irish and UK time (GMT)**.

| Reported area / identifiers | Project response and evidence | Remaining gap |
| --- | --- | --- |
| Functionality: 1.1, 1.2, 1.4, 1.9, 1.12, 1.13, 1.15, 1.19 | Hosted Stripe checkout; verified signed webhook logic; pending/paid separation; safe cart reconciliation/retries; author-owned blog CRUD; additional private PetProfile model and complete frontend CRUD; regression tests; detailed local/Render instructions. See checkout/, accounts/, blog/, docs/TESTING.md. | A real sandbox payment and deployed webhook/Cloudinary/email/database verification have not been performed here. The identifiers are grouped because the supplied summary does not provide every official descriptor. |
| UX/design: 2.3 and requested process improvements | Correct links, responsive layouts, meaningful headings, safe image fallbacks; new **retrospective** wireframes; accurate ERD; feature stories with priority/status. See docs/design/, docs/MODELS.md, docs/USER_STORIES.md. | Catalogue products still need accurate authorised photos; fallback art is not a product photograph. Original historical planning is not available. GitHub issue/label updates require available API access; no fictitious issues were created. |
| SEO: 3.1, 3.5, 3.6 | Served robots and sitemap use configured Render host; route tests verify public entries; public canonicals exclude query strings; distinct escaped titles/descriptions; private pages have noindex. | Read-only checks against the actual deployed revision and external validators remain pending. Static crawler copies are secondary artifacts; live endpoints are generated from templates/data. |
| Authorisation: 4.6 | Author/staff checks on direct GET and POST for blog edit/delete; private owner-filtered pet profiles and order history; CSRF on mutations. | Local tests and browser flows verify these paths; repeat acceptance against the approved deployment. |
| Marketing: 5.1 | Removed unverified social links. Replaced the misleading title-card claim with a new, clearly labelled Facebook-page **design mockup** and genuine local render. Newsletter validation preserved. See docs/marketing/ and docs/ASSETS.md. | No published Facebook URL, live page screenshot or marketing results are claimed. A mockup addresses the format described in the supplied feedback; acceptance remains the assessor's decision. |
| Business model: 6.1 (previously passed) | README retains B2C audience, conversion path, community/content and proposed consented marketing explanation. | Owner must verify final catalogue accuracy, claims and image rights. No invented metrics or campaigns. |
| Additional schema/design evidence | Current Mermaid ERD includes actual models and relations. New wireframes are explicitly dated retrospective design review artifacts. | Do not misrepresent them as the project's original pre-development planning. |

## Additional custom model and frontend

`PetProfile` is distinct from product/order checkout models. A member supplies their pet's name, species, care focus and optional notes, sees a corresponding routine prompt, and manages their own profiles through the website. Ownership is assigned server-side and enforced on list, form and mutation queries. BlogPost and Subscriber remain present; the new profile feature provides the additional custom model requested in the supplied summary. `CheckoutState` is a separate internal payment coordinator; it is **not** offered as the user-facing custom-feature evidence.

## Honest evidence boundaries

- Unit/integration-style Django tests use an isolated database and offline mocked Stripe/upload adapters. Real HMAC signature verification and application state transitions are exercised.
- Local browser evidence uses synthetic users, stories/products and, where stated, paid-order fixtures. A fixture marked paid is not evidence of a payment being processed.
- Genuine local renders of new designs are evidence of those designs, not an existing Facebook page, original historical wireframes or live campaigns.
- Build/deployment-settings smoke checks are local; they cannot prove actual Render PostgreSQL, external TLS, Stripe, Cloudinary or SMTP configuration.
- Review docs/TESTING.md for actual command outcomes and docs/EVIDENCE.md for owner-required records. No private assessor correspondence or secret values should be committed.
