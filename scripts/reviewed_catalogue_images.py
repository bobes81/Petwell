"""Owner-operated, dry-run-first image replacement; never uploads or migrates.

May be copied to an approved private operator location and run from the existing
Petwell application root. Its dependencies already exist in deployed f75dbe1.
Importing this module does not configure Django or connect to any database.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys


def _read_guard(path):
    from products.catalogue import ImageMappingError, MAX_MANIFEST_BYTES

    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(descriptor, "rb") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_MANIFEST_BYTES:
                raise ValueError
            raw = stream.read(MAX_MANIFEST_BYTES + 1)
        if len(raw) > MAX_MANIFEST_BYTES:
            raise ValueError
        return json.loads(raw, object_pairs_hook=unique_keys)
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise ImageMappingError("Guard must be a bounded regular non-symlink JSON file.") from None


def _query():
    from django.db.models import TextField
    from django.db.models.functions import Cast
    from products.catalogue import PHYSICAL_PRODUCT_NAMES
    from products.models import Product

    return Product.objects.filter(name__in=PHYSICAL_PRODUCT_NAMES).annotate(
        reviewed_raw_image=Cast("image", output_field=TextField())
    ).order_by("pk")


def _database_fingerprint():
    from django.db import connection

    config = connection.settings_dict
    identity = {"vendor": connection.vendor, "host": config.get("HOST"),
                "port": str(config.get("PORT", "")), "name": str(config.get("NAME"))}
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()


def snapshot():
    """SELECT only. Keep the resulting reference/ID record private."""
    import cloudinary
    from django.conf import settings
    from products.catalogue import ImageMappingError, PHYSICAL_PRODUCT_NAMES

    cloud = cloudinary.config().cloud_name
    if not cloud or settings.CLOUDINARY_STORAGE.get("CLOUD_NAME") != cloud:
        raise ImageMappingError("Verify the existing SDK/storage cloud before snapshotting.")
    products = list(_query())
    if len(products) != 9 or {p.name for p in products} != PHYSICAL_PRODUCT_NAMES:
        raise ImageMappingError("Expected one existing record per physical name; resolve missing/duplicate names privately.")
    if any(not p.reviewed_raw_image for p in products):
        raise ImageMappingError("This replacement review expects existing non-empty images. Review empty fields separately.")
    return {
        "schema_version": 1,
        "cloud_name": cloud,
        "database_fingerprint": _database_fingerprint(),
        "products": [{
            "product_id": p.pk,
            "product_name": p.name,
            "expected_image_reference": p.reviewed_raw_image,
            "replace_approved": False,
        } for p in products],
    }


def review(manifest_path, guard_path, images_dir, *, apply=False):
    """Validate sources/identity/current references; update only approved images."""
    import cloudinary
    from django.conf import settings
    from django.db import transaction
    from products.catalogue import ImageMappingError, validate_image_plan

    cloud, mappings = validate_image_plan(manifest_path, images_dir)
    guard = _read_guard(guard_path)
    if (
        type(guard) is not dict or set(guard) != {"schema_version", "cloud_name", "database_fingerprint", "products"}
        or type(guard["schema_version"]) is not int or guard["schema_version"] != 1
        or guard["cloud_name"] != cloud
        or guard["database_fingerprint"] != _database_fingerprint()
        or cloudinary.config().cloud_name != cloud
        or settings.CLOUDINARY_STORAGE.get("CLOUD_NAME") != cloud
        or type(guard["products"]) is not list or len(guard["products"]) != 9
    ):
        raise ImageMappingError("Review a complete schema-1 guard for the same cloud and intended database connection profile.")
    expected = {}
    fields = {"product_id", "product_name", "expected_image_reference", "replace_approved"}
    planned = {item["product_id"]: item for item in mappings}
    for number, row in enumerate(guard["products"], 1):
        if (
            type(row) is not dict or set(row) != fields
            or type(row["product_id"]) is not int or row["product_id"] not in planned
            or row["product_id"] in expected
            or row["product_name"] != planned[row["product_id"]]["product_name"]
            or type(row["expected_image_reference"]) is not str
            or not 1 <= len(row["expected_image_reference"]) <= 255
            or type(row["replace_approved"]) is not bool
        ):
            raise ImageMappingError(f"Guard entry {number}: exact identity, original reference and explicit boolean approval required.")
        expected[row["product_id"]] = row
    if set(expected) != set(planned):
        raise ImageMappingError("Guard identities must match the complete reviewed image manifest.")
    approved = sum(row["replace_approved"] for row in expected.values())
    if apply and not approved:
        raise ImageMappingError("No product replacements are explicitly approved; nothing was changed.")

    def inspect(products):
        if len(products) != 9:
            raise ImageMappingError("The physical catalogue changed; obtain a new review.")
        todo = []
        already = preserved = 0
        for product in products:
            item = planned.get(product.pk)
            if item is None or item["product_name"] != product.name:
                raise ImageMappingError("Product identity changed; obtain a new review.")
            row = expected[product.pk]
            if not row["replace_approved"]:
                preserved += 1
            elif product.reviewed_raw_image == item["reference"]:
                already += 1
            elif product.reviewed_raw_image != row["expected_image_reference"]:
                raise ImageMappingError("An approved image changed since review; no replacements saved.")
            else:
                todo.append((product.pk, product.name, row["expected_image_reference"], item["reference"]))
        return todo, already, preserved

    if apply:
        with transaction.atomic():
            todo, already, preserved = inspect(list(_query().select_for_update()))
            for product_id, name, old, new in todo:
                changed = _query().filter(
                    pk=product_id, name=name, reviewed_raw_image=old,
                ).update(image=new)
                if changed != 1:
                    raise ImageMappingError("Concurrent image conflict; all replacements rolled back.")
    else:
        todo, already, preserved = inspect(list(_query()))
    return {
        "mode": "APPLIED" if apply else "DRY_RUN",
        "images_changed" if apply else "images_would_change": len(todo),
        "already_matching": already,
        "unapproved_preserved": preserved,
        "scope": "Only explicitly approved Product.image references; no uploads/fetches, record creation/deletion or migrations.",
        "limitations": "Owner must verify remote image content, returned upload metadata, rights and product accuracy separately.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("snapshot", "review", "apply"), nargs="?", default="review")
    parser.add_argument("--manifest")
    parser.add_argument("--guard")
    parser.add_argument("--images-dir", default="docs/catalogue/concepts")
    options = parser.parse_args()
    if options.mode != "snapshot" and (not options.manifest or not options.guard):
        parser.error("review/apply require --manifest and --guard")
    if not Path("manage.py").is_file():
        parser.error("Run from the existing Petwell application root.")
    sys.path.insert(0, str(Path.cwd()))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "petwell.settings")
    import django
    django.setup()
    from django.db import connection
    if connection.vendor != "postgresql":
        parser.exit(1, "Operator CLI requires the explicitly verified PostgreSQL target, not a SQLite fallback.\n")
    from products.catalogue import ImageMappingError
    try:
        result = snapshot() if options.mode == "snapshot" else review(
            options.manifest, options.guard, options.images_dir, apply=options.mode == "apply",
        )
    except ImageMappingError as error:
        parser.exit(1, str(error) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
