"""Prepare empty-only catalogue image associations; never upload assets."""

import cloudinary
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Length

from products.catalogue import ImageMappingError, validate_image_plan
from products.models import Product


class Command(BaseCommand):
    help = (
        "Validate nine local AI illustrations and existing Cloudinary references. "
        "Dry-run by default; --apply fills empty image fields only. No upload or fetch."
    )

    def add_arguments(self, parser):
        parser.add_argument("manifest")
        parser.add_argument("--images-dir", required=True)
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        try:
            cloud_name, mappings = validate_image_plan(
                options["manifest"], options["images_dir"]
            )
        except ImageMappingError as error:
            raise CommandError(str(error)) from None
        if (
            cloudinary.config().cloud_name != cloud_name
            or settings.CLOUDINARY_STORAGE.get("CLOUD_NAME") != cloud_name
        ):
            raise CommandError(
                "The manifest cloud must match the configured Cloudinary cloud. "
                "No provider connection was attempted."
            )
        if options["apply"]:
            with transaction.atomic():
                products = self._products(mappings, lock=True)
                changed, skipped = self._apply(mappings, products)
            self.stdout.write(
                f"Applied: {changed} empty image fields filled; "
                f"{skipped} existing images preserved. No upload or fetch performed."
            )
        else:
            products = self._products(mappings)
            changed = sum(not products[item["product_id"]].image for item in mappings)
            self.stdout.write(
                f"DRY RUN: {changed} empty image fields would be filled; "
                f"{len(mappings) - changed} existing images would be preserved. "
                "No database writes, uploads or fetches performed."
            )
        self.stdout.write(
            "Local file validity and owner attestations are checked. "
            "Remote asset existence, rights and product accuracy are not verified."
        )

    def _products(self, mappings, lock=False):
        query = Product.objects.filter(
            pk__in=[item["product_id"] for item in mappings]
        ).order_by("pk")
        if lock:
            query = query.select_for_update()
        products = {product.pk: product for product in query}
        for number, item in enumerate(mappings, 1):
            product = products.get(item["product_id"])
            if product is None or product.name != item["product_name"]:
                raise CommandError(
                    f"Entry {number}: the existing product ID and exact name do not match."
                )
        return products

    def _apply(self, mappings, products):
        changed = skipped = 0
        for item in mappings:
            if products[item["product_id"]].image:
                skipped += 1
                continue
            # CloudinaryField prepares a falsy RHS as None; image="" therefore
            # cannot reliably select a real legacy SQL empty string.
            count = Product.objects.annotate(image_length=Length("image")).filter(
                Q(image__isnull=True) | Q(image_length=0),
                pk=item["product_id"], name=item["product_name"],
            ).update(image=item["reference"])
            if count != 1:
                raise CommandError(
                    "A product changed during application; all associations were rolled back."
                )
            changed += 1
        return changed, skipped
