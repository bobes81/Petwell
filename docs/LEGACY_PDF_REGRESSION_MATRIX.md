# Regression acceptance matrix: unavailable legacy products

**Updated scope:** PR #9 implements availability guards and preserves history. The original acceptance matrix below is retained; local automated results are recorded in [the PR #9 review](PR9_REVIEW_AND_RELEASE_GATES.md). A1–A8, A10, A12–A15 have offline regression coverage. A9/A16 retain provider/cutover acceptance work; A11 needs the approved real-record operator check. No production withdrawal or external payment acceptance is claimed.

| ID | Scenario | Expected result |
| --- | --- | --- |
| A1 | New physical product with default availability | Visible in shop and purchasable; preserve existing behaviour |
| A2 | Archived legacy PDF in catalogue | Not offered in public product listing |
| A3 | POST direct add-to-cart for archived product ID | No cart mutation; safe unavailable response/message |
| A4 | Existing session cart contains archived product | Cart page does not crash or count it as payable; clear removal path |
| A5 | Checkout POST with archived product still in cart | Reject before creating Order or Stripe Session; preserve cart and explain removal |
| A6 | Paid order history references archived product | Historical OrderItem, quantity and price remain visible and unchanged |
| A7 | Buy Again includes both archived and active products | Only active product added, no silent charge for archived item |
| A8 | Buy Again includes only archived product | No new purchasable item; clear notice |
| A9 | Existing Stripe Session predates archival | Do not assume hiding product cancels payment; review state and fulfilment obligation |
| A10 | Migration against historical database | All Product IDs, OrderItems, order totals, image refs and customer history preserved |
| A11 | Repeat archive operation | Idempotent; does not overwrite unrelated products |
| A12 | New seed run | Does not recreate or reactivate legacy PDF |
| A13 | Existing product price <= 0 | Remains unpurchasable, independent of availability |
| A14 | Existing 404/nonexistent product ID | No change to cart; avoid leaking information |
| A15 | Unauthenticated and authenticated checkout | Same availability validation for both |
| A16 | Concurrent checkout/archival | No new payable session for withdrawn offer after effective cutover; document pending-session handling |

## Implementation constraints

- Explicitly identify the actual legacy record before archiving; never identify it solely by its assumed numeric ID.
- Default availability should preserve existing physical catalogue records. Use a data migration or a separately approved management command to archive only verified non-deliverable offers; avoid automatically hiding all products containing the substring `PDF` if legitimate future downloads may exist.
- The production write is **not authorised** by this test matrix.
- A test-only fixture should include a paid OrderItem pointing to an archived Product and assert historical integrity.
- Cover GET/POST semantics and CSRF protection already enforced on cart mutations.
- Keep Stripe disabled until fulfilment decision and real sandbox acceptance; avoid payment-related external calls in unit tests.
- Update `docs/LEGACY_PDF_CHECKOUT_BLOCKER.md` once implementation and tests actually pass; do not label a proposed test as passed.

The code and synthetic migration tests now run; exact-head SQLite/PostgreSQL CI must be verified after push. The existing owner real-data rehearsal completed five earlier migrations, so only the later products.0002 needs a targeted new local real-data check. Actual record withdrawal and issued Stripe Session reconciliation remain separately approved owner actions.
