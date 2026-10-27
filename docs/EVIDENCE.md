# Genuine submission evidence checklist

These are tasks/placeholders, not completed evidence. Do not fabricate reports, diagrams, screenshots, social metrics or test outcomes. Remove any unfinished claim before submission and identify any remaining limitation honestly.

| Evidence | What to supply | Status |
| --- | --- | --- |
| Assessor feedback and rubric mapping | Map each returned assessment issue to code, test and evidence | TODO: owner must supply actual feedback/rubric |
| Wireframes | Original planning files, or clearly dated retrospective diagrams labelled as such; homepage/shop/cart/checkout/blog/order history on mobile and desktop | TODO |
| Schema diagram | [Implemented model diagram](MODELS.md), reflecting this revision rather than historical planning | Added; review against assessment rubric |
| Responsive screenshots | Deployed pages at phone/tablet/desktop widths, real navigation expanded/collapsed, no overflow | Local Chromium examples added in TESTING.md; deployed screenshots still TODO |
| Stripe test checkout | Sandbox hosted page and confirmed in-app order; redact credentials, personal details and payment identifiers as needed | TODO after authorised deployment |
| Webhook evidence | Test event delivery with HTTP 200 and matching paid order; duplicate delivery not duplicating an order | TODO |
| Blog permissions and CRUD | Own post create/edit/delete, image retention/validation, non-owner direct URL denial, staff moderation | TODO |
| My orders / Buy again | Two users, isolated histories, paid reorder using a changed current price | TODO |
| Automated tests | Save actual command, date, test count and output from the submitted commit | Local results documented in TESTING.md; rerun final commit |
| Accessibility and validators | Real W3C/Lighthouse/keyboard/contrast findings and fixes, with dates and page URLs | TODO |
| Facebook business page | Genuine published page URL, page overview/about details, actual product/community posts and screenshots | TODO; a mockup is not a published page |
| Marketing evidence | Actual dated posts/strategy; only report reach/engagement where measured | TODO |
| Image/source credits | Verify each used asset's source and permission, including legacy assets | TODO |

Place genuine files under a chosen `docs/evidence/` directory and link them from README/TESTING with captions and dates once available. Do not include customer data, account tokens, keys, dashboard signing secrets or card information. The existing `static/images/ facebook-mockup-petwell.png` is named as a mockup and must not be presented as proof of a live Facebook page.

Suggested order before the 31 October 2026, 12:00 UK deadline: review assessor feedback → review code/tests → configure test integrations → explicitly approve deployment → run deployed acceptance checks → capture evidence → check README links and final submitted commit.
