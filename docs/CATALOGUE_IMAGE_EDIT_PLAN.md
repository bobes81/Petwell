# Catalogue image derivatives — preparation only

Prepared **30 October 2026** following the owner's request for a clean catalogue. This document authorises no production update, deployment, merge, asset deletion or overwrite. No image has been edited or uploaded as part of this plan.

## Originals and permitted scope

Use the nine exact original PNGs under [catalogue/concepts](catalogue/concepts), with their [recorded source hashes](catalogue/README.md). Keep every source byte and existing Cloudinary asset unchanged. Work on separate derivative files in a separate directory; never save over the originals. Product ID 5 (the PDF) is excluded.

For each derivative, remove only the embedded `PRODUCT CONCEPT` header wording and the complete `AI-generated illustration · not a real product photograph` footer. Retain the Petwell brand, exact product title, container labels, product drawing, shadows, background and composition. Remove a header separator only if it would otherwise be left dangling. Preserve the full **1000 × 1000** canvas; do not crop, stretch, upscale or redraw the product. Do not add packaging details, certifications, ingredients or efficacy claims.

**Additional visible wording:** seven bottle/jar/pouch illustrations also have an internal `AI CONCEPT` label. Dental Chew Sticks and Eco Toy Rope do not have this internal label. The current requested header/footer edit leaves internal labels intact. Any wider removal should be explicitly included in the reviewed edit scope before execution; do not silently change product/container lettering.

## Edit and acceptance process

1. Establish small, per-image masks covering only the approved text and anti-aliased edges. Review the masks before editing; do not use a whole-canvas generation request or a single broad rectangle across the product/title.
2. Remove text locally and restore the existing background within those masks. If an edit tool changes pixels outside the approved regions or changes product identity, reject that output rather than accept a plausible new drawing. No paid tool, subscription or new charge is authorised.
3. Save a separate lossless PNG derivative. Check dimensions, PNG decoding and colour mode; compute its new SHA-256. Compare decoded original/derivative pixels: changes must remain inside the approved masks. A changed derivative hash is expected and must not be represented as the original source hash.
4. Inspect each derivative at native size and in desktop/mobile card previews. Confirm exact title, unchanged product identity, clean background with no text fragments, consistent composition and no clipping. Keep original-versus-derivative evidence and record the mask/review result. Visual approval does not establish supplier packaging accuracy or independently prove licensing.
5. Preserve truthful provenance and the README **AI Tools** acknowledgement. The outputs remain AI-assisted concept illustrations, not real product photographs. Do not describe them as supplier photography after the visible labels are removed. Owner approval to use the sources is recorded; independent rights verification has not been established here.

## New assets and separate production mapping

After derivative review and the corresponding upload approval, use only the existing cloud `dr3kwknli` within its available no-charge capacity. Request **unused new** public IDs beneath `petwell/ai-products/`, for example `<original-slug>-clean-20261030-<unique-suffix>`. This is a naming pattern, not an existing asset ID or upload result. Retaining the namespace preserves existing contain fitting. Require `overwrite: false`, image resource type and upload delivery; do not delete or modify the earlier uploads or placeholders. Stop on a collision, ambiguous upload controls or a paid prompt.

Capture actual returned public IDs, positive versions, PNG format and original secure URLs. Open each actual original URL and match the accepted derivative; where accessible, compare decoded image pixels or an unchanged byte hash. Metadata alone does not establish image content. No derivative upload results exist yet.

Prepare a **new private derivative manifest**, keeping the prior original-image manifest intact. Use the derivative filename/hash and a provenance record linking the original filename/hash, approved edits and owner review. The reviewed validator can use a separate directory of the nine derivative sources; do not replace the originals merely to satisfy validation. Actual IDs/versions must come from the new uploads. Only product IDs **1, 2, 3, 4, 6, 7, 8, 9 and 10** are targets.

Then follow the [existing guarded reference procedure](CATALOGUE_PLACEHOLDER_REPLACEMENT.md): a fresh snapshot from the intended operator connection, exact old-to-new review, read-only dry-run and **separate explicit production-write approval**. Do not fabricate a connection fingerprint from the Render database resource ID. Preserve prices, names, descriptions, availability, order/item links and PDF ID 5. No migration is required. The current supplied production observations report 10 products, 6 orders and 6 items; they are a dated baseline, not a reason to reject legitimate later orders or restore the entire database.

## Shortest release path and present blockers

- Finish/review the chosen derivative set **before** changing production references, avoiding two successive image mappings. Keep the earlier original-upload plan available; do not execute it implicitly while derivatives are being prepared.
- This Codex context still has no authenticated production database or Cloudinary connector. Access reported in the separate ChatGPT context does not transfer here. That authorised operator must perform the provider checks/uploads and fresh helper snapshot/review. The previously prepared guard is deliberately incomplete and is not a successful operator dry-run.
- Changing only image references requires no application deployment. The separate removal of the duplicate HTML caption was pushed in application commit `182e007ab7d6e7fddeb5f95d81d00e00cdfcccc7`; it is not deployed. That UI change needs its own owner-approved deployment, and it does not remove embedded PNG wording.
- After any separately approved mapping, inspect the actual live desktop/mobile catalogue and retain genuine evidence. No live image fix, final submission readiness or Pass is claimed by this plan.
