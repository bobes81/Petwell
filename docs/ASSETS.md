# Asset inspection and evidence limits

This is an inventory of observations made from repository files on **28 October 2026**, not a licence grant, proof of ownership, or a marketing result. No images were generated, edited, rebranded, or presented as newly captured evidence for this inspection. Preserve visible provenance marks.

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

### Catalogue-photo readiness checklist

The following inventory records the ten names in the seed inspected on 28 October, not a verified deployed catalogue. On 29 October the unsupported PDF was removed from **future seeding**, leaving nine physical sample offers; existing database rows were not changed. The seed supplies **no image for any entry**. Existing database records may differ; inspect them after authorised access instead of inferring their state from the seed.

| Seed product | Image and rights evidence |
| --- | --- |
| Calming Lavender Spray | Not supplied |
| Dental Chew Sticks | Not supplied |
| Joint Support Treats | Not supplied |
| Hypoallergenic Shampoo | Not supplied |
| Mindful Pet Journal (PDF), legacy seed only | Omitted from new seeding; existing rows preserved. Any existing offer needs an actual file and verified fulfilment process, or removal from the offered catalogue. |
| Organic Paw Balm | Not supplied |
| Digestive Support Powder | Not supplied |
| Eco Toy Rope | Not supplied |
| Herbal Ear Cleaner | Not supplied |
| Herbal Chill Drops | Not supplied |

For each retained catalogue item, record the exact product name, image creator/source URL or owner reference, permission/licence and any required attribution, the date checked, and its uploaded image reference. Do not publish private supplier agreements or account credentials. Match the image to the actual item; a branded supplier photo requires permission, and a photo of an unrelated item does not resolve the gap. Also review descriptions and wellness claims for accuracy.

After an approved upload, inspect shop/cart/reorder pages on desktop and mobile, confirm the correct image and readable alternative text, and check the missing-image fallback separately. Save actual results and captions with the date and deployed revision. No catalogue image, permission or external upload is marked complete by this document.

## Submission and marketing evidence

- The Facebook-named title card is not a Facebook UI mockup or proof that a page exists. The new [clearly labelled proposal](marketing/facebook-mockup.html) and [genuine local rendering](marketing/facebook-mockup.png) are design evidence only. If claiming a published page, supply its verified URL and actual, dated page/post screenshots. Do not imply that publication occurred merely because the mockup exists.
- Never claim reach, engagement, sales or campaign delivery from these files. Only include statistics that were actually measured.
- Existing `docs/evidence/local-*.png` files are genuine **local-development** screenshots from the earlier implementation. They show neither production deployment nor live payment/marketing integration and must retain that label.
- Keep original planning files and clearly label any retrospective wireframes. The owner supplied a private feedback summary; it is intentionally not committed. The official full guide was not available in the checkout. The project's own [assessment map](ASSESSMENT_REVIEW.md) and [evidence checklist](EVIDENCE.md) record the remaining review without publishing private correspondence.
- Check each used asset's rights and add real attribution where required. No guessed licence, fabricated supplier claim or removed provenance mark should be used to fill an evidence gap.

See [TESTING.md](TESTING.md) for tested behaviour and the outstanding deployed checks, and [EVIDENCE.md](EVIDENCE.md) for the remaining submission checklist.
