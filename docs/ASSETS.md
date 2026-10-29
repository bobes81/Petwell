# Asset inspection and evidence limits

This records the legacy-file inspection on **28 October 2026** and the separately supplied concept-illustration review on **29 October 2026**. It is not a licence grant, proof of ownership, or a marketing result. No images were generated, edited, rebranded, or presented as newly captured website evidence for these inspections. Preserve visible provenance marks.

## Files actually inspected

| Repository path | What the file visibly contains | Suitable use / limitation |
| --- | --- | --- |
| `static/images/ facebook-mockup-petwell.png` | A blue PetWell / “Pet Wellness & Care” title card, with a visible **MINIMAX / Hailuo AI** watermark. It contains no Facebook page interface, posts, account URL or metrics. | May be described as an existing watermarked title-card asset, subject to source/rights review. It is **not** evidence of a Facebook business page or published campaign. The filename is misleading. |
| `static/images/ header.png` | The same title card and watermark. Its SHA-256 is identical to the Facebook-named file, confirming these are duplicate file contents. | Duplicate legacy artwork, not an independent screenshot or separate piece of evidence. |
| `static/images/candle.png` | A decorative candle with dogs on it and a visible **MINIMAX / Hailuo AI** watermark. | Not proof of a manufactured product, a supplier photograph or the origin of any listed wellness item. Do not assign it to an unrelated product. |
| `static/images/tshirt-frenchbulldog.png` | A close-up dog portrait with a visible **MINIMAX / Hailuo AI** watermark; no T-shirt is visible. | The name does not describe the visible content. Do not present it as a photograph of an actual T-shirt for sale. |

All four inspected files are 1280×720 PNGs. The first two filenames begin with a literal space. The duplicate title-card SHA-256 is `a4ace5f21f10bfd680fd8c4e2b046e04fca25afcd0eac9bb63543a96ef3522ac`. These observations identify what the files show; they do not establish the account that created them, the tool's terms, or permission to use them commercially.

Other legacy images in `static/images/` have filenames suggesting family, happiness, shop/cart/blog screenshots, apparel and candles. **They were not all visually reviewed in this inspection.** A filename, existing Git history or a watermarked picture does not establish permission or accuracy. Do not assign licence terms or claim source attribution without checking the actual source records.

## Product image behaviour

The current `Product.image` field stores a Cloudinary reference. A local file with a similar name is not automatically linked to a product. The existing `products.seed.run()` creates sample wellness products without images, so a local placeholder is expected for those records. The safe image URL filter and browser error fallback prevent a missing Cloudinary configuration or unavailable image URL from breaking the page.

A fallback makes the interface usable; it does not supply a genuine product photograph. Before presenting real products, review each product's actual identity, description and price, supply an accurate image you own or have permission to use, record the source and permission, and upload it through the configured admin/Cloudinary workflow. Do not use the decorative candle or dog portrait as an invented photograph of a sample balm, spray or shampoo.

### Catalogue-image readiness checklist

The following inventory records the ten names in the seed inspected on 28 October, not a verified deployed catalogue. On 29 October the unsupported PDF was removed from **future seeding**, leaving nine physical sample offers; existing database rows were not changed. The seed supplies **no image for any entry**. Existing database records may differ; inspect them after authorised access instead of inferring their state from the seed.

| Seed product | Image and rights evidence |
| --- | --- |
| Calming Lavender Spray | [Owner-supplied AI concept](catalogue/concepts/calming-lavender-spray.png); inspected, usage approval pending |
| Dental Chew Sticks | [Owner-supplied AI concept](catalogue/concepts/dental-chew-sticks.png); inspected, usage approval pending |
| Joint Support Treats | [Owner-supplied AI concept](catalogue/concepts/joint-support-treats.png); inspected, usage approval pending |
| Hypoallergenic Shampoo | [Owner-supplied AI concept](catalogue/concepts/hypoallergenic-shampoo.png); inspected, usage approval pending |
| Mindful Pet Journal (PDF), legacy seed only | Omitted from new seeding; existing rows preserved. Any existing offer needs an actual file and verified fulfilment process, or removal from the offered catalogue. |
| Organic Paw Balm | [Owner-supplied AI concept](catalogue/concepts/organic-paw-balm.png); inspected, usage approval pending |
| Digestive Support Powder | [Owner-supplied AI concept](catalogue/concepts/digestive-support-powder.png); inspected, usage approval pending |
| Eco Toy Rope | [Owner-supplied AI concept](catalogue/concepts/eco-toy-rope.png); inspected, usage approval pending |
| Herbal Ear Cleaner | [Owner-supplied AI concept](catalogue/concepts/herbal-ear-cleaner.png); inspected, usage approval pending |
| Herbal Chill Drops | [Owner-supplied AI concept](catalogue/concepts/herbal-chill-drops.png); inspected, usage approval pending |

For each retained catalogue item, record the exact product name, image creator/source URL or owner reference, permission/licence and any required attribution, the date checked, and its uploaded image reference. Do not publish private supplier agreements or account credentials. Match the image to the actual item; a branded supplier photo requires permission, and a photo of an unrelated item does not resolve the gap. Also review descriptions and wellness claims for accuracy.

After an approved upload, inspect shop/cart/reorder pages on desktop and mobile, confirm the correct image and readable alternative text, and check the missing-image fallback separately. Save actual results and captions with the date and deployed revision. No production image association, usage approval or external upload is marked complete by this document.

### Nine supplied AI concepts — 29 October follow-up

At `d8203e0`, no nine source files had been supplied. The owner subsequently supplied `Petwell_9_product_concepts.zip` on 29 October. Its nine original PNG byte streams are now prepared under [catalogue/concepts](catalogue/README.md), with a [prepared draft manifest](catalogue/catalogue-images.DRAFT.json) and [inspection record](evidence/29oct-uploaded-concepts-inspection.json). All nine images decode successfully as **1000 × 1000 RGB PNGs**, and all nine distinct SHA-256 hashes match the supplied draft. Archive path/member checks and CRC integrity passed.

The visible product names match the nine physical names in the repository exactly. Each image uses an appropriate generic product/container icon, is labelled **AI CONCEPT**, and carries a footer explaining that it is not a real product photograph. This establishes the supplied files' labels and conceptual subject matching, not actual packaging, formulations, efficacy, current production database identities or supplier endorsement.

The package describes them as original AI-concept graphics created on 29 October 2026. That is an owner/package provenance claim: the PNG metadata contains no generator, authorship or licence evidence, and no generation tool/version or applicable usage terms were supplied. Rights and the owner's final accuracy approval remain pending; `rights_reviewed` stays false. Product IDs, cloud name, Cloudinary public IDs and upload versions remain unset. No external upload or existing product image was changed.

The earlier phrase “genuine-photo requirement” overstated the supplied feedback: it identifies placeholders, without specifying photographs. Accurate authorised illustrations can be reviewed as a candidate; do not guarantee assessment acceptance or describe them as actual supplier/product photographs.

[CATALOGUE_IMAGES.md](CATALOGUE_IMAGES.md) separates source-only local validation of the prepared draft from the complete dry-run-first, empty-fields-only association workflow. The blank template remains a general example. A later owner-reviewed upload must retain provenance, use new unique public IDs and preserve existing assets. Mapped `petwell/ai-products/` images are explicitly captioned as AI-generated illustrations. Source hashes validate local files, not ownership or an actual Cloudinary upload. The legacy PDF remains a separate fulfilment decision, with its database/history untouched.

## Submission and marketing evidence

- The Facebook-named title card is not a Facebook UI mockup or proof that a page exists. The new [clearly labelled proposal](marketing/facebook-mockup.html) and [genuine local rendering](marketing/facebook-mockup.png) are design evidence only. If claiming a published page, supply its verified URL and actual, dated page/post screenshots. Do not imply that publication occurred merely because the mockup exists.
- Never claim reach, engagement, sales or campaign delivery from these files. Only include statistics that were actually measured.
- Existing `docs/evidence/local-*.png` files are genuine **local-development** screenshots from the earlier implementation. They show neither production deployment nor live payment/marketing integration and must retain that label.
- Keep original planning files and clearly label any retrospective wireframes. The owner supplied a private feedback summary; it is intentionally not committed. The official full guide was not available in the checkout. The project's own [assessment map](ASSESSMENT_REVIEW.md) and [evidence checklist](EVIDENCE.md) record the remaining review without publishing private correspondence.
- Check each used asset's rights and add real attribution where required. No guessed licence, fabricated supplier claim or removed provenance mark should be used to fill an evidence gap.

See [TESTING.md](TESTING.md) for tested behaviour and the outstanding deployed checks, and [EVIDENCE.md](EVIDENCE.md) for the remaining submission checklist.

Final framing check: the existing cover fit cropped source concepts at phone widths. A scoped AI-image contain fit now preserves all source pixels at 390/430/768/1440 in [the isolated CSS preview](evidence/29oct-concept-css-preview.json). The readable external AI caption remains. This is local presentation evidence, not actual Cloudinary upload/association, product accuracy or rights approval.
