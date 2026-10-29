# Safe product-image association and legacy PDF decision

Updated on 29 October 2026 after the owner supplied `Petwell_9_product_concepts.zip`. [Nine unchanged PNG concepts and the prepared draft](catalogue/README.md) are now included for review: exact nine physical catalogue names, 1000×1000 RGB PNG, all source hashes matched. All files were individually viewed and visibly disclose AI/product-concept status. [Measured inspection](evidence/29oct-uploaded-concepts-inspection.json). These are generic concept illustrations, not product photographs or verified packaging. No Cloudinary upload or product association occurred.

The [blank template](catalogue-images.example.json) remains available for another package. The [source-filled draft](catalogue/catalogue-images.DRAFT.json) retains null product IDs/versions, blank cloud/public IDs and `rights_reviewed: false`. The creation date/tool/rights are source claims rather than independently established by empty PNG metadata. Owner review and actual remote/record metadata remain necessary.

The private feedback summary identifies placeholder product images; it does not specify that the media must be photographs. Accurate, authorised AI illustrations are a candidate, subject to the actual guide/assessor's acceptance. Do not present them as supplier photographs, proof of actual packaging or a guaranteed Pass. Local visual title/concept/disclosure review is complete; actual product accuracy, source terms and rights approval remain pending.

## What the command safely prepares

`associate_product_images` validates a private, explicit nine-item manifest and defaults to **read-only dry-run**. It never creates products, uploads/downloads assets, calls Cloudinary APIs or seeds data. Only a later explicit `--apply` can fill empty `Product.image` fields; no production invocation was performed here.

- The manifest itself must be a regular, non-symlink JSON file of at most 64 KiB; FIFO/device/directory inputs are rejected before opening.
- All nine entries must match the intended physical names and explicit existing primary keys. Duplicate IDs, references or source hashes and incomplete/extra entries are rejected before writes. No product IDs are guessed from seed order.
- The manifest's cloud name must match the configured SDK/storage cloud, without printing credential values. The full `CLOUDINARY_URL` stays private; a public cloud name is not the credential URL.
- Each local source must be an actual JPEG, PNG or WEBP of at most 5 MiB, with its matching SHA-256. Only regular files directly in the chosen directory are accepted; path escapes/symlinks are rejected. Record actual source/tool/date and applicable usage terms in `provenance`, and confirm rights/accuracy only after review. An attestation is not independent proof of rights.
- References use **new, prospective** `petwell/ai-products/` public IDs, a positive upload version and `jpg`, `png` or `webp` matching the decoded file. No delivery URL, credential URL, query string or transformation is accepted. This namespace labels mapped shop images “AI-generated product illustration”; it does not describe an existing upload.
- Application locks/rechecks the selected records and conditionally fills only NULL/empty image references in one transaction. Existing non-empty images are skipped, even if the manifest differs; there is no force/overwrite option. Names, descriptions, prices, product IDs, order links and files are preserved. An unexpected write conflict aborts the operation.

File validation and a public ID cannot prove that the Cloudinary asset exists, matches the source file or renders correctly. A later approved upload/browser check is still required. The command makes no migration, so it does not invalidate the completed owner-reported schema rehearsal.

## Completed local source check, without invented identifiers

```bash
python manage.py associate_product_images docs/catalogue/catalogue-images.DRAFT.json --images-dir docs/catalogue/concepts --sources-only --settings=petwell.test_settings
```

This explicit read-only mode checks files, exact catalogue names, hashes, dimensions/format and source attestations without querying a database, reading provider configuration or constructing remote references. It accepts declared pending fields and reports rights still unapproved. It cannot be combined with `--apply`; normal full dry-run/application continues to reject the incomplete draft. It is **not** a Cloudinary check, product-identity match or ready-to-apply result. [Actual preflight output](evidence/29oct-uploaded-concepts-preflight.txt) was captured with SQL, sockets and provider access refused. No database IDs were invented to make validation pass.

## Smallest owner workflow, without overwriting existing data

1. The nine source files are now preserved in Git; keep the private source/usage records and originals backed up. Review each illustration against the exact retained product; do not invent packaging, certifications or medical benefits. Retain provenance marks and disclose AI generation. Keep private backups of the originals and existing image references.
2. After separate approval, use the existing Cloudinary account within its available no-charge limits. Upload under **new unique** public IDs in `petwell/ai-products/`, with replacement/overwrite disabled. If an identifier already exists, stop and choose a new one. Do not overwrite existing assets or enable paid features. Privately record each returned `public_id`, `version` and format; this review did not upload or verify them.
3. Copy the source-filled draft (or the blank template for a different package) to a private location as `catalogue-images.private.json` (that basename is ignored by Git). Fill the actual cloud name, product IDs/names, source basenames, hashes, provenance and exact returned upload metadata. `rights_reviewed` remains false until review; `ai_generated: true` is the intended media type, not evidence of a supplied file. The PDF is not an image target.
4. Rehearse the manifest on a **separate disposable local database** with matching product IDs, using ordinary development settings and the intended private Cloudinary configuration for URL construction. Keep production `DATABASE_URL` unset and choose the local target explicitly. Do not point a test runner at a valuable restored database. `petwell.rehearsal_settings` intentionally disables Cloudinary, so it cannot validate this account mapping. Neither the ordinary local profile nor the command should be assumed to block all other provider actions.

   ```bash
   python manage.py associate_product_images /private/path/catalogue-images.private.json --images-dir /private/path/originals --settings=petwell.settings
   ```

   This validates and reports a dry-run; the placeholder template must fail safely. Review all nine matches and the fill/skip counts. A wrong/missing name or an existing image requires review rather than an automatic replacement. For local hash calculation use `shasum -a 256` (macOS) or `sha256sum` (Linux) on the actual files; do not publish the private manifest or source records merely to complete this step.
5. On that disposable local database only, repeat the same reviewed command with `--apply`, then inspect the shop on desktop/mobile and confirm each exact image, AI caption, HTTPS URL and missing-image fallback. Re-running is non-destructive. The command does not automatically delete Cloudinary assets if the local transaction fails.
6. **Production application is a separate approval and write.** After the selected release, fresh backup and explicit owner approval, first run the dry-run against the verified intended target, review the current fill/skip result, then apply the same reviewed manifest only if authorised. Do not infer that local IDs still match production. Verify the approved site's nine image associations and keep genuine redacted evidence. This task does not authorise that step now.

If a product already has an image, this workflow preserves it. A legitimate replacement needs a separately reviewed backup/replace plan; do not clear the field to bypass the guard. The image command is not part of `build.sh`, migrations or automatic deployment.

## Legacy PDF: preserve history and resolve the offer

The old `Mindful Pet Journal (PDF)` record may still exist among the ten restored products. New seeding omits it, but **no production record was deleted, hidden, renamed or changed**. The application has no download file/delivery implementation. Reviewed PR #9 adds `Product.is_available` and guards catalogue, direct cart POST, stale carts, checkout and Buy Again; history is preserved. The default is True for every existing row, so neither this migration nor the image workflow automatically withdraws the PDF. Payment confirmation does not send a PDF.

The smallest safe decision is one of these owner-controlled choices **before enabling checkout**:

| Owner's actual situation | Safe strategy |
| --- | --- |
| An actual authorised PDF exists and can genuinely be delivered | Privately verify the file and a manual fulfilment process, describe the real delivery method/timeframe accurately, and test receipt using controlled data before offering it. Do not promise instant download. This review does not claim a file or process exists. |
| No deliverable PDF or process exists | Keep checkout unavailable until an approved operator verifies the exact row and outstanding obligations, then explicitly sets `is_available=False` after the new availability migration and selected code are deployed with approval. Preserve Product/OrderItem records. The new `products.0002` requires one targeted local real-data rehearsal; do not repeat the five completed migrations unnecessarily. |

Merely hiding a card in the shop is incomplete: direct add-to-cart URLs, existing carts and “Buy again” can still reference the product. Setting its price to zero or deleting order history is not withdrawal. The reviewed availability guards cover shop, direct cart mutations, existing cart validation, reorder and checkout. Withdrawal must still account for already-issued payable Stripe Sessions; changing a field cannot invalidate a hosted URL or discard valid signed payment evidence. Preserve paid/pending records and resolve any genuine existing obligation privately; do not manually relabel orders paid or assume all legacy purchases were paid.

Do not enable payment configuration to work around this decision. No new delivery feature, refund, payment, record deletion or production catalogue change was performed.

See [ASSETS.md](ASSETS.md) for the honest legacy inventory and [RENDER_CHECKLIST.md](RENDER_CHECKLIST.md) for Cloudinary/Gmail/Stripe acceptance and release gates. A clearly labelled Facebook mockup remains acceptable in the supplied feedback; a new published page is not added as another task.

Availability validation guards a new request against the committed catalogue state; it is not a provider-wide transaction barrier. Before declaring a withdrawal effective, an approved operator must pause/drain in-flight checkout requests and reconcile already-issued hosted Sessions. Do not assume a flag closes a Stripe URL, hold database locks over provider I/O, or discard a valid signed payment event. Concurrent withdrawal/provider acceptance is an operational gate, not a claimed automated external pass.

Final local presentation review found that ordinary cover-style cards cropped these square concepts on mobile. AI-mapped images now use scoped contain fitting, preserving the full source and separate AI caption; ordinary product images retain their styling. [Measured before/after CSS preview](evidence/29oct-concept-css-preview.json) uses the nine originals in data URLs, not database assignments, Cloudinary or a deployed shop. Source bytes/hashes, rights flags and operational IDs are unchanged.
