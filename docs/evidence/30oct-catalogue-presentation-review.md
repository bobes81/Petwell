# Catalogue presentation review — 30 October 2026

## Scope and verification boundary

The owner requested removal of unnecessary prominent AI labels while preserving truthful product information and README acknowledgement. Production is owner-reported at `f75dbe1`; inspecting that commit confirms a conditional `AI-generated product illustration` HTML paragraph immediately below each image in the reserved AI namespace. The same paragraph existed in the current branch. It is not part of the product name or description.

The live shop request was blocked by this environment's proxy before reaching Render. Therefore this is a source-code review of the deployed commit, not a newly verified live screenshot or claim about which production references have been applied.

## Artwork and minimal change

All nine original PNGs have been visually inspected and their exact hashes verified against the supplied ZIP and pinned Git source. Each has an embedded `PRODUCT CONCEPT` header and `AI-generated illustration · not a real product photograph` footer. Some also show an internal `AI CONCEPT` label. These are image pixels, not HTML; removing the HTML paragraph does not remove them. [Original inventory and visual-review boundaries](../catalogue/README.md), [original inspection record](29oct-uploaded-concepts-inspection.json).

The uploaded asset metadata matches those nine names, but exact remote image bytes/visuals have not been independently checked here: CDN requests were blocked by the proxy. Do not infer successful remote visual acceptance from metadata alone. The owner/operator must open each uploaded original URL and confirm the expected artwork and full footer.

The PR removes only the redundant per-card HTML paragraph. It retains image alt text, names, descriptions, prices, cart controls, Bootstrap responsive columns, fixed card-image height and scoped `object-fit: contain` for concept images. Original PNGs, Cloudinary references, database fields, migrations and assets are unchanged. README retains AI-assisted-work acknowledgement and now distinguishes embedded disclosure from the removed duplicate caption.

## Checks and deployment implication

[33 targeted image-association/source/replacement tests passed](30oct-catalogue-presentation-tests.txt); Django's test-run system check found no issues. Coverage includes mixed ordinary/concept image fitting, product identity/alt text, source integrity and guarded replacement behavior. No full suite or new browser/responsive acceptance run is claimed for this small template change.

A separately approved **application deployment is required** for the HTML-caption removal to appear on the live site. This is a presentation improvement, not a prerequisite for the already prepared data-only image-reference correction. No deployment, production write, upload, overwrite, deletion or merge was executed. Removing embedded wording would require separately approved new derivative artwork/assets; originals must remain intact, and no such work is authorised or performed here.
