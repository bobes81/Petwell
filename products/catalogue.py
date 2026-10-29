"""Validate an owner's private image plan without uploading or fetching assets."""

import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import stat
import warnings

from cloudinary import CloudinaryResource
from PIL import Image


PHYSICAL_PRODUCT_NAMES = frozenset({
    "Calming Lavender Spray",
    "Dental Chew Sticks",
    "Joint Support Treats",
    "Hypoallergenic Shampoo",
    "Organic Paw Balm",
    "Digestive Support Powder",
    "Eco Toy Rope",
    "Herbal Ear Cleaner",
    "Herbal Chill Drops",
})
AI_IMAGE_PREFIX = "petwell/ai-products/"
PUBLIC_ID_PATTERN = re.compile(r"petwell/ai-products/[A-Za-z0-9_-]+\Z")
MAX_SOURCE_BYTES = 5 * 1024 * 1024
MAX_MANIFEST_BYTES = 64 * 1024
ENTRY_FIELDS = {
    "product_id", "product_name", "source_file", "sha256", "provenance",
    "rights_reviewed", "ai_generated", "public_id", "version", "format",
}


class ImageMappingError(ValueError):
    """A safe message that never includes manifest contents or private paths."""


def _read_source(directory, filename, entry_number):
    if (
        not isinstance(filename, str)
        or filename in {"", ".", ".."}
        or Path(filename).name != filename
        or "/" in filename or "\\" in filename
        or any(ord(character) < 32 for character in filename)
    ):
        raise ImageMappingError(
            f"Entry {entry_number}: source_file must be a plain filename."
        )
    path = directory / filename
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise OSError
        # O_NOFOLLOW prevents a file being swapped to a symlink before open.
        flags = (
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as source:
            opened = os.fstat(source.fileno())
            if (
                not stat.S_ISREG(opened.st_mode)
                or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
                or opened.st_size > MAX_SOURCE_BYTES
            ):
                raise OSError
            contents = source.read(MAX_SOURCE_BYTES + 1)
        if not contents or len(contents) > MAX_SOURCE_BYTES:
            raise OSError
    except (OSError, ValueError):
        raise ImageMappingError(
            f"Entry {entry_number}: source must be a regular, non-symlink "
            "local file of at most 5 MiB."
        ) from None
    return contents


def validate_image_plan(manifest_path, images_directory, *, sources_only=False):
    """Check sources and, by default, require a complete association plan.

    Source-only validation permits declared pending identity/provider fields;
    it does not construct delivery references or verify owner attestations.
    """
    try:
        path = Path(manifest_path)
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise OSError
        flags = (
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as source:
            opened = os.fstat(source.fileno())
            if (
                not stat.S_ISREG(opened.st_mode)
                or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
                or opened.st_size > MAX_MANIFEST_BYTES
            ):
                raise OSError
            raw = source.read(MAX_MANIFEST_BYTES + 1)
        if len(raw) > MAX_MANIFEST_BYTES:
            raise ValueError
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError
                result[key] = value
            return result

        manifest = json.loads(raw, object_pairs_hook=unique_object)
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise ImageMappingError(
            "The private manifest must be a regular, non-symlink file "
            "containing bounded valid JSON."
        ) from None
    if (
        not isinstance(manifest, dict)
        or set(manifest) != {"schema_version", "cloud_name", "products"}
        or type(manifest["schema_version"]) is not int
        or manifest["schema_version"] != 1
        or not isinstance(manifest["cloud_name"], str)
        or not (
            re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,49}", manifest["cloud_name"])
            or (sources_only and manifest["cloud_name"] == "")
        )
        or not isinstance(manifest["products"], list)
        or len(manifest["products"]) != 9
    ):
        raise ImageMappingError(
            "Use schema_version 1, a valid or permitted pending cloud name "
            "and exactly nine product entries."
        )
    directory = Path(images_directory)
    try:
        if directory.is_symlink() or not directory.is_dir():
            raise OSError
        directory = directory.resolve(strict=True)
    except (OSError, ValueError):
        raise ImageMappingError("Select an existing non-symlink image directory.") from None

    checked = []
    seen_ids, seen_names, seen_public_ids, seen_hashes = set(), set(), set(), set()
    for number, entry in enumerate(manifest["products"], 1):
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
            raise ImageMappingError(f"Entry {number}: fields do not match schema 1.")
        valid_product_id = (
            type(entry["product_id"]) is int
            and 0 < entry["product_id"] <= 9223372036854775807
        )
        valid_public_id = (
            isinstance(entry["public_id"], str)
            and bool(PUBLIC_ID_PATTERN.fullmatch(entry["public_id"]))
        )
        valid_version = (
            type(entry["version"]) is int
            and 0 < entry["version"] <= 9223372036854775807
        )
        if (
            not (valid_product_id or (sources_only and entry["product_id"] is None))
            or not isinstance(entry["product_name"], str)
            or entry["product_name"] not in PHYSICAL_PRODUCT_NAMES
            or type(entry["rights_reviewed"]) is not bool
            or (not sources_only and entry["rights_reviewed"] is not True)
            or entry["ai_generated"] is not True
            or not isinstance(entry["provenance"], str)
            or not 1 <= len(entry["provenance"].strip()) <= 1000
            or not isinstance(entry["sha256"], str)
            or not re.fullmatch(r"[a-f0-9]{64}", entry["sha256"])
            or not (valid_public_id or (sources_only and entry["public_id"] == ""))
            or not (valid_version or (sources_only and entry["version"] is None))
            or not isinstance(entry["format"], str)
            or entry["format"] not in {"jpg", "png", "webp"}
        ):
            raise ImageMappingError(
                f"Entry {number}: complete the identity, source, rights review "
                "and versioned AI-image reference."
            )
        if (
            (valid_product_id and entry["product_id"] in seen_ids)
            or entry["product_name"] in seen_names
            or (valid_public_id and entry["public_id"] in seen_public_ids)
            or entry["sha256"] in seen_hashes
        ):
            raise ImageMappingError(
                f"Entry {number}: product IDs, names, image IDs and source hashes "
                "must be distinct."
            )
        contents = _read_source(directory, entry["source_file"], number)
        if hashlib.sha256(contents).hexdigest() != entry["sha256"]:
            raise ImageMappingError(f"Entry {number}: source SHA-256 does not match.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(contents)) as image:
                    width, height = image.size
                    actual_format = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}.get(
                        image.format
                    )
                    if actual_format != entry["format"]:
                        raise ValueError
                    image.verify()
                with Image.open(BytesIO(contents)) as image:
                    image.load()
        except (OSError, ValueError, SyntaxError, EOFError, Image.DecompressionBombError,
                Image.DecompressionBombWarning):
            raise ImageMappingError(
                f"Entry {number}: source is not a valid matching JPEG, PNG or WEBP image."
            ) from None
        checked_entry = {
            "product_id": entry["product_id"],
            "product_name": entry["product_name"],
            "source_file": entry["source_file"],
            "sha256": entry["sha256"],
            "format": entry["format"],
            "width": width,
            "height": height,
            "rights_reviewed": entry["rights_reviewed"],
        }
        if not sources_only:
            reference = CloudinaryResource(
                public_id=entry["public_id"], version=entry["version"],
                format=entry["format"], resource_type="image", type="upload",
            ).get_prep_value()
            if len(reference) > 255:
                raise ImageMappingError(f"Entry {number}: image reference is too long.")
            checked_entry["reference"] = reference
        checked.append(checked_entry)
        if valid_product_id:
            seen_ids.add(entry["product_id"])
        seen_names.add(entry["product_name"])
        if valid_public_id:
            seen_public_ids.add(entry["public_id"])
        seen_hashes.add(entry["sha256"])
    if seen_names != PHYSICAL_PRODUCT_NAMES:
        raise ImageMappingError("The plan must cover the nine physical sample products.")
    return manifest["cloud_name"], checked
