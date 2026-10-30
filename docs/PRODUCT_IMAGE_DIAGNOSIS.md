# Product image diagnosis — 30 October 2026

The owner verified that all ten production products have Cloudinary references, but the live shop displays fallback images. The reported shape `image/upload/v1771237247/<public-id>.png` is a valid CloudinaryField persisted reference. **Do not assume the assets are missing or rewrite the records.** The production public image URL and actual CDN response remain unverified; this environment's public shop request was proxy-blocked before reaching Render.

## Confirmed repository finding and narrow fix

The deployed helper reads `image.url`, which works for the CloudinaryResource returned by a normal database query. With a configured cloud, the example persisted shape already produces `https://res.cloudinary.com/<configured-cloud>/image/upload/v1771237247/<public-id>.png`. There is no evidence that this ordinary path duplicates `image/upload`.

However, a **plain string** supplied by an unsaved model/form/template context always selected the static placeholder. The helper now parses such strings using the SDK's CloudinaryField parser, preserving version, format and folder semantics; resource rendering explicitly keeps HTTPS and retains its options without mutation. Empty/unsafe references and absent cloud configuration still use the local fallback. No cloud name, asset ID or upload version is invented, no network request is made and no database reference changes.

[Actual baseline/fixed comparison](evidence/30oct-image-url-baseline-comparison.json) uses synthetic offline values. [Focused tests](evidence/30oct-image-focused-tests.txt) check the **initial img src**, not merely whether a placeholder string occurs in HTML: every working image also includes a placeholder in its browser `onerror` handler. This fix hardens a confirmed input case; it is **not proof that plain strings caused the reported production failure**.

## Smallest owner read-only check — existing deployed site

1. Open **View Page Source** for `/products/` and locate a product's original `<img src=...>`. Inspect the original HTML, because the browser can replace a failed remote `src` with the SVG after loading. Do not submit a form or modify a product.
2. Classify that original `src`:

   | Original HTML / response | Meaning and next action |
   | --- | --- |
   | `/static/images/placeholder...svg` | Server selected the fallback before any image request. Privately verify cloud configuration and reference rendering; a stored path alone does not prove a configured cloud name. |
   | HTTPS Cloudinary delivery URL | URL construction occurred. Inspect that exact URL's network response before calling the asset missing. |
   | Wrong cloud, doubled upload prefix, missing version/extension or HTTP URL | Compare the URL with the stored reference and actual Cloudinary metadata; record the specific mismatch, not a guessed replacement. |

3. Open the **unsigned public HTTPS image delivery URL** in a new tab and inspect browser Network status, `Content-Type` and any `X-Cld-Error`. Do not share `CLOUDINARY_URL`, credentials, signed URLs or token parameters. A Mac can use this read-only alternative after setting `PUBLIC_IMAGE_URL` to that actual public delivery URL:

   ```bash
   curl --proto '=https' --max-time 15 --silent --show-error --head -- "${PUBLIC_IMAGE_URL:?}"
   ```

   A proxy/tunnel connection failure is not a Cloudinary asset response. A HEAD response alone is not full image-decode/browser acceptance.
4. For an actual CDN response:

   - **200 with an image:** inspect decoding, browser Console/Network, cache and the initial URL. A browser error can still explain the fallback; do not change database records without evidence.
   - **404:** owner privately compares the configured cloud and exact public ID/version/format with the existing account's Media Library. It can indicate wrong metadata/account as well as a missing asset; it is not permission to invent an ID or upload a replacement.
   - **401/403:** owner reviews access/delivery restrictions and resource type. Do not expose signing secrets, automatically make a private asset public or treat a proxy denial as asset denial.

## Read-only command on the reviewed new code

The new `diagnose_product_images` command uses **SELECTs and local URL generation only**. It performs no fetch/upload, payment, environment change or database write. It reports whether a cloud name exists, whether storage/SDK cloud names agree and whether each reference produces an initial placeholder or delivery URL. It does not certify asset existence or rights.

After a separately approved manual deployment of the new code, use an already available Render command route, or an explicitly approved local read-only connection/configuration. Do not buy a shell/service. The deployed `f75dbe1` does not contain this command. Never use the rehearsal profile to diagnose real Cloudinary configuration: it intentionally disables Cloudinary.

```bash
python manage.py diagnose_product_images --settings=petwell.settings
# Optional: include only unsigned HTTPS res.cloudinary.com image/upload URLs.
python manage.py diagnose_product_images --show-public-urls --settings=petwell.settings
```

Default output contains no raw references or credential values. The opt-in excludes query tokens, signatures and private/authenticated URLs; keep even public-URL reports private until reviewed. An actual reviewed ID can narrow output with `--product-id`; do not guess one.

`cloud_name_unavailable` requires owner review of the existing private Render configuration. `storage_cloud_matches_sdk=false` requires reviewing conflicting configuration sources, not switching accounts automatically. Public delivery requires a correct cloud name; API credentials are needed for uploads, not for constructing a normal public delivery URL. The SDK's documented separate-variable precedence still applies. This task does not authorise any environment change.

## If an external correction is genuinely required

The owner must verify the existing account's actual asset metadata and product accuracy/rights first. If data/configuration is wrong, prepare and separately approve the exact correction with its original value preserved. If an asset is genuinely absent, separately approve an authorised original upload and explicit mapping; do not fabricate replacement imagery. [The existing image workflow](CATALOGUE_IMAGES.md) preserves **non-empty** references and cannot replace all ten already-filled fields. Do not clear fields to bypass that guard. No production record, Cloudinary asset or environment value was changed here.

A new manual Render deployment is required to use the helper hardening/diagnostic command. **Redeployment alone is not a proven cure for the current live fallback:** the given normal database reference already renders correctly offline, and the actual public URL/configuration/asset response still needs the above check. Auto-deploy is disabled according to the owner; do not merge or deploy as part of this investigation.
