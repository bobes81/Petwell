"""Inspect rendering/configuration only; never fetch, upload or change images."""

import json
from urllib.parse import urlsplit

import cloudinary
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import TextField
from django.db.models.functions import Cast
from django.templatetags.static import static

from blog.media import image_url
from products.models import Product


def public_delivery_url(url):
    """Do not print credential URLs, signed tokens or arbitrary stored text."""
    parsed = urlsplit(url)
    parts = parsed.path.strip("/").split("/")
    if (
        parsed.scheme == "https"
        and parsed.netloc == "res.cloudinary.com"
        and not parsed.query
        and not parsed.fragment
        and len(parts) >= 4
        and parts[1:3] == ["image", "upload"]
        and not any(part.startswith("s--") for part in parts[3:])
    ):
        return url
    return None


class Command(BaseCommand):
    help = (
        "Read-only product image rendering diagnosis. No provider requests or writes. "
        "Remote asset existence and browser delivery are not verified."
    )

    def add_arguments(self, parser):
        parser.add_argument("--product-id", type=int)
        parser.add_argument(
            "--show-public-urls", action="store_true",
            help="Include only unsigned HTTPS res.cloudinary.com image/upload URLs; keep the report private.",
        )

    def handle(self, *args, **options):
        product_id = options["product_id"]
        if product_id is not None and (
            type(product_id) is not int or not 0 < product_id <= 9223372036854775807
        ):
            raise CommandError("Use an actual positive product ID; do not guess it.")
        query = Product.objects.annotate(
            stored_image=Cast("image", output_field=TextField())
        ).order_by("pk")
        if product_id is not None:
            query = query.filter(pk=product_id)
        cloud = cloudinary.config().cloud_name
        placeholder = static("images/placeholder.svg")
        rows = []
        for product in query.values("pk", "stored_image"):
            reference = product["stored_image"]
            # Match the field conversion used by the actual product queryset,
            # while still reporting malformed references without printing them.
            try:
                resource = CloudinaryField("image").to_python(reference)
            except (AttributeError, TypeError, ValueError):
                resource = None
            url = image_url(resource)
            is_placeholder = url == placeholder
            row = {
                "product_id": product["pk"],
                "reference_present": bool(reference),
                "initial_src_is_placeholder": is_placeholder,
                "status": (
                    "no_reference" if not reference else
                    "cloud_name_unavailable" if is_placeholder and not cloud else
                    "reference_not_renderable" if is_placeholder else
                    "delivery_url_generated"
                ),
            }
            if options["show_public_urls"]:
                safe = public_delivery_url(url)
                if safe:
                    row["public_delivery_url"] = safe
            rows.append(row)
        if product_id is not None and not rows:
            raise CommandError("The selected product was not found. Nothing was changed.")
        self.stdout.write(json.dumps({
            "mode": "READ_ONLY_NO_NETWORK",
            "cloud_name_configured": bool(cloud),
            "storage_cloud_matches_sdk": settings.CLOUDINARY_STORAGE.get("CLOUD_NAME") == cloud,
            "products_checked": len(rows),
            "products": rows,
            "limitations": [
                "No database fields, environment values or SDK settings were changed.",
                "No Cloudinary API, upload or image fetch was performed.",
                "A generated URL is not evidence that an asset exists or is publicly accessible.",
                "Browser onerror can replace a failed remote src; inspect the original HTML and network response.",
                "Unsigned public URLs are included only with --show-public-urls. No raw references or credentials are printed.",
            ],
        }, indent=2))
