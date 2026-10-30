# Replace reviewed catalogue placeholder references — owner approval required

Prepared **30 October 2026**; deadline **31 October at 12:00 UK time**. No upload, production write, deployment, merge or paid resource was performed. This is an owner-operated procedure, not approval to execute it.

**Later presentation request:** the owner requested a plan for new derivatives without the embedded concept header/footer. Follow [the derivative edit plan](CATALOGUE_IMAGE_EDIT_PLAN.md) before choosing the final asset set. Earlier instructions here to retain embedded wording describe the original set; originals and existing assets must still remain untouched. No derivative edit/upload or production mapping is executed or authorised by this planning note.

## Latest owner authorisation and access boundary

On **30 October**, the owner authorised the supplied nine AI-labelled originals **conditional on verifying accuracy and usage rights**, and authorised new non-overwriting uploads only if authorised access and existing no-charge capacity are available. This is not approval for production image-reference writes. The owner also supplied independently checked production product IDs; a private working manifest now binds those IDs by exact name to the nine original files and cloud `dr3kwknli`. **Mindful Pet Journal (PDF), ID 5, is excluded and must not be modified by this image task.** The public historical source draft stays unchanged; neither supplied IDs nor a source-only pass substitute for a fresh original-reference snapshot.

The reviewer inspected all nine originals again: exact catalogue titles and AI/not-a-photograph footers match, PNG dimensions/hashes pass, and no original was edited. Actual supplier packaging, ingredients, efficacy and physical fulfilment are not certified by these generic drawings. The source archive/handoff claims AI concepts and Python/Pillow drawing but supplies no independently verifiable author licence or generation/source terms. **Conditional use approval is recorded; rights verification is still blocked, so `rights_reviewed` remains false.** The minimum missing source record is who created/provided the artwork, which tools/assets/fonts were used and the applicable permission/terms allowing this website use. Do not invent a licence or request private account credentials in chat.

No Cloudinary connector, configured Cloudinary credentials or authenticated owner account is available in this workspace. Consequently, existing correct assets, current quota, upload permissions and returned URLs **have not been checked**; no upload was attempted. A public delivery URL cannot enumerate an account or establish rights. The owner must use the existing authenticated account, or provide an approved secure access route, to perform section A after resolving rights. New IDs/versions must come from real provider results. Source-only validation of the private ID-filled draft passed for all nine; **the production mapping dry-run is blocked** until actual metadata, rights review and the fresh private original-reference guard exist. No production connection was made to obtain that guard.

Fastest safe handoff: **iPad** — confirm source rights/accuracy, inspect the existing cloud and available no-charge capacity, upload approved originals as new assets, then open each returned original URL. **MacBook or an already available authorised operator shell** — complete the private manifest, capture originals, run section B's read-only review, and submit the exact nine old→new associations for separate owner approval before any section C write. Keep original references and all operational review files private. No application deployment is required for this correction.

## What the new evidence establishes

**Later owner account check, 30 October:** the owner logged into `dr3kwknli (Test)`, saw 114 assets, found the construction graphic by searching `zsag3ghgmsfhmjnzn9a9`, and found no results for `calming-lavender-spray`. These are owner-reported observations, not a reviewer account inspection. The empty search does not rule out a correct asset stored under another ID. The owner's browser session has not granted the reviewer access; no authenticated Cloudinary tool/session/credentials are available here.

For **Calming Lavender Spray**, the owner opened the original HTML delivery URL in Chrome:

`https://res.cloudinary.com/dr3kwknli/image/upload/v1771237419/zsag3ghgmsfhmjnzn9a9.png`

It displayed PetWell's **“Our website is under construction – Images will be available soon”** graphic, not the intended product illustration. The exact origin HTTP status was not captured. The reviewer's attempted fetch was blocked by the environment's proxy before reaching Cloudinary. [Dated observation](evidence/30oct-cloudinary-placeholder-observation.json).

This confirms a wrong-image association/content for that observed product: constructing a plausible Cloudinary URL is not enough. Do not declare the asset missing or assume the other eight physical products have the same artwork without reviewing them. Keep the original asset intact.

## Smallest solution — no application deploy required for mapping

1. Owner reviews/approves the nine supplied source concepts, their usage rights and product accuracy.
2. After separate upload approval, reuse any **verified correct existing** matching assets, or create new uniquely identified assets in the **existing** cloud. Never overwrite/delete the old assets.
3. After reviewing actual returned metadata and a dry-run, owner explicitly approves changing only the selected existing `Product.image` values. Preserve all product IDs, names, descriptions, prices, availability flags, orders and item links.

Deployed **`f75dbe1` already contains** CloudinaryField URL rendering, the `petwell/ai-products/` AI-illustration caption and the CSS contain fit for these concepts. New valid versioned references are read on the next normal shop request. No new migration, service, environment change or manual Render deployment is required **for this data-only correction**. The raw-string hardening/diagnostic in `0940446` is a separate improvement and is not the cure for placeholder artwork served by a valid asset URL.

The existing `associate_product_images` command deliberately preserves all non-empty images. It will not fix these already-filled fields. **Do not clear them or add a force flag.** The separately reviewed [operator helper](../scripts/reviewed_catalogue_images.py) below provides explicit approval, an exact original-reference guard, database-profile binding, transaction/row locks and conditional image-only updates. It uploads/fetches nothing and does not migrate or deploy.

## A. Owner-approved source and Cloudinary steps

### Short browser route while reviewer access is unavailable

Use the [nine proposed unique IDs](catalogue/cloudinary-upload.PROPOSED.json). **These are requested new names, not existing assets or upload results.** Keep them separate from the real mapping manifest; do not copy a proposed name into its `public_id` until the provider actually returns that exact value. Verify each requested ID is unused immediately before upload; stop on any collision. A random suffix reduces collision risk but cannot prove absence remotely.

1. Confirm source rights/accuracy and the existing account's available no-charge capacity. Conditional approval is not a verified rights record. Stop at any upgrade/payment prompt; do not change account/upload presets.
2. Start with `calming-lavender-spray.png` in Media Library's **Upload** local-file flow. Where the upload panel exposes **Advanced / Public ID**, enter its complete proposed ID, without `.png`, and require overwrite disabled. Leave the original file uncropped/unconverted. UI labels vary: if the controls do not expose the full ID/non-overwrite setting clearly, stop and report the visible options rather than guessing or changing existing assets. Merely selecting an asset folder does not guarantee the required public-ID prefix.
3. Inspect that newly returned asset's details: actual `public_id` starts `petwell/ai-products/`, resource type `image`, delivery type `upload`, positive version and `png` format. Open the **original delivery URL**, verify the exact title and complete AI footer. Preserve every existing asset. A successful upload alone does not fix the website.
4. When that succeeds, repeat for the other eight original PNGs. Do not include the PDF. Collect actual original delivery URLs/public IDs/versions for review; these public values may be shared without API credentials. Keep database guards and completed production manifests private.
5. Complete section B only with actual verified metadata and a fresh original-reference snapshot. Run **review**, not **apply**, then obtain separate exact-mapping approval. No upload or production dry-run has yet been executed by the reviewer.

- Use the nine unchanged PNGs in [the verified inventory](catalogue/README.md) and [prepared source draft](catalogue/catalogue-images.DRAFT.json). They are 1000×1000 **AI-generated product concepts, not photographs**. Keep both the in-image concept/AI disclosure and site caption; do not crop the footer or promise actual packaging/ingredients/efficacy from a generic illustration. Rights/accuracy approval is still pending; the draft correctly has `rights_reviewed: false`.
- In the existing owner's Cloudinary account, verify the intended cloud against the observed **`dr3kwknli`** and deployed configuration. No key/secret or credential URL belongs in a manifest, screenshot or chat. Do not create an account/service or upgrade a plan; stop if the existing available no-charge allowance cannot accommodate the approved files.
- Review each current physical product image before deciding replacement. Only Calming Lavender Spray's wrong artwork is newly confirmed. For each target, verify the candidate illustration's exact title matches its catalogue name. Exclude **Mindful Pet Journal (PDF)**: there is no tenth concept/file or automatic PDF withdrawal.
- **Upload approval covers only the needed original files, up to nine**, as new image resources with public `upload` delivery and unused public IDs beneath `petwell/ai-products/`. Disable overwrite/use new unique IDs. An existing asset-folder label does not necessarily create that public-ID prefix in dynamic-folder accounts: verify the **actual returned public ID**. If UI behavior cannot ensure preservation, stop rather than overwrite. Existing correct assets may be reused only when their actual identity/format/version/source and required AI namespace are verified; do not copy/rename an existing asset implicitly.
- Privately record the **actual** cloud name, returned `public_id`, positive upload `version`, format `png`, resource type `image` and delivery type `upload`. No proposed slug, folder name, inferred version or guessed ID is an upload result.
- Open each exact new/reused delivery URL **before changing product records**. Verify the correct product title/artwork and AI footer, not the construction graphic. Record genuine results/HTTP status when available; a path/public ID alone is not acceptance.

## B. Prepare two private review files

Use an existing owner-authorised command route on the intended database: an already available Render Shell, or a privately verified operator connection. No paid shell/resource is required or authorised. For the no-deploy route, copy the reviewed helper to a private temporary location; do not edit the deployed application files/start command. Run it from the existing application root containing `manage.py`, with the existing production settings. Verify service **`srv-d67jptusb7us73e9qbj0`** and database privately; never use a valuable restored database as production or guess product IDs.

The helper CLI rejects SQLite fallback. Snapshot includes a fingerprint of the connection profile (not credentials); applying a guard exported from another profile/database is refused. A fingerprint is not a substitute for the operator checking the actual intended service/target.

**Read-only preparation** (choose a new private directory and preserve existing review files):

```bash
umask 077
mkdir /tmp/petwell-image-review
# Copy the approved helper here and verify its SHA-256 before running it.
(
  set -C  # refuse to overwrite an existing private original-reference record
  python /tmp/petwell-image-review/reviewed_catalogue_images.py snapshot \
    > /tmp/petwell-image-review/catalogue-image-guard.private.json
)
```

Stop after any directory/copy/checksum/command error; choose a fresh private directory rather than overwriting an earlier guard. Expected: nine existing physical names with **actual product IDs**, exact original stored image references and `replace_approved: false`. No SQL writes, upload or fetch occurs. Missing/duplicate names, empty references or cloud mismatch means stop. Keep this guard private: it is also the original image-reference record for any separately approved image-only recovery.

Copy the [source draft](catalogue/catalogue-images.DRAFT.json) to `/tmp/petwell-image-review/catalogue-images.private.json`. Complete its real product IDs **by exact name from the snapshot**, actual cloud/upload metadata, source provenance and owner-reviewed rights flags. The manifest remains nine entries; do not add the PDF or fabricate metadata for any entry. Complete/verify this plan before a batch write; an incomplete plan is deliberately refused. For any record whose current image should remain, retain `replace_approved: false` in the guard.

In the guard, owner sets `replace_approved: true` only for the exact rows whose current/reference and proposed new illustration have been reviewed. Initially approving just Calming Lavender Spray allows a one-product smoke change; the others remain untouched. Do not edit the captured original references or database fingerprint to bypass a mismatch.

```bash
python /tmp/petwell-image-review/reviewed_catalogue_images.py review \
  --manifest /tmp/petwell-image-review/catalogue-images.private.json \
  --guard /tmp/petwell-image-review/catalogue-image-guard.private.json \
  --images-dir docs/catalogue/concepts
```

Expected: `DRY_RUN`, the intended `images_would_change` count and preserved/unapproved count. The source validator checks all nine original files/hashes/formats, rights attestations, exact names/IDs, AI namespace and matching cloud. Dry-run checks original raw references, including versions/extensions; it does not verify remote content. Only approve the write after this exact plan and all target image URLs are reviewed. Do not post either private JSON file to Git or chat.

## C. Separately approved image-only mapping

**Do not run this preparation-only step until the owner approves the specific mapping/database write.** Pause other product-admin edits for this short transaction; this does not require another schema cutover or another payment. Images are not part of the frozen Stripe payment payload, and existing order data is not rewritten.

```bash
python /tmp/petwell-image-review/reviewed_catalogue_images.py apply \
  --manifest /tmp/petwell-image-review/catalogue-images.private.json \
  --guard /tmp/petwell-image-review/catalogue-image-guard.private.json \
  --images-dir docs/catalogue/concepts
```

Expected: only approved `Product.image` references change. The helper locks/rechecks the physical rows, refuses an unexpectedly changed original reference and rolls back the whole transaction on a conflict. Repeating an unchanged successful operation reports already-matching images and makes no further update. Unapproved rows and the PDF are preserved. No records/assets are created/deleted by this helper; Cloudinary uploads are a separate preceding owner action.

Verify the smoke product on desktop/mobile: correct illustration, title, full AI footer/caption and new original HTML URL. Privately compare product fields and order/item counts/links before/after. After genuine success, owner may approve the remaining reviewed entries and repeat review/apply; already-mapped entries remain no-ops. Do not repeat a sandbox payment just to test image mapping. Stop on any mismatch or uncertain image identity.

For recovery, retain the private original guard and exact applied manifest. Any reverse operation requires separate approval, verifies that the current image is still the just-applied new reference and restores **only that image column**. Never restore a whole database over later orders or delete the new/old Cloudinary assets as a shortcut.

## Local evidence and execution boundary

[11 synthetic focused regressions](evidence/30oct-reviewed-image-replacement-tests.txt) cover read-only snapshot/review, exact identity/cloud/database/approval guards, version-only staleness, image-only/history preservation, one-product smoke/batch continuation, idempotence and atomic rollback. This is not an executed production mapping or upload. [Source-only preflight](evidence/30oct-placeholder-source-preflight.txt) validates the nine unchanged originals; rights and real operational metadata remain unapproved/unset in the public draft.

Reviewed operator-helper SHA-256: `703db8281b5abe3a0a7b3d4a97ff4641e0ce8d9b309bbbf5102cbee14cd99cda`. Recheck the copied helper before executing; this value does not identify any Cloudinary asset or production record.
