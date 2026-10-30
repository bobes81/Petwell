"""Render Cloudinary references without changing stored data or fetching assets."""

from urllib.parse import urlsplit

from cloudinary import CloudinaryResource
from cloudinary.models import CloudinaryField
from django.templatetags.static import static


def image_url(image):
    # Database reads normally return CloudinaryResource. Unsaved model/form
    # values and explicit template contexts can still contain the stored string.
    # Parse the SDK's persisted format; treating it as a public_id would duplicate
    # image/upload and lose the original version semantics.
    if isinstance(image, str):
        image = image.strip()
        if not image or ":" in image or image.startswith("/") or any(
            char in image for char in ("?", "#", "\n", "\r")
        ):
            return static("images/placeholder.svg")
        try:
            image = CloudinaryField("image").to_python(image)
        except (AttributeError, TypeError, ValueError):
            return static("images/placeholder.svg")
    if image:
        try:
            if isinstance(image, CloudinaryResource):
                if ":" in image.public_id or image.public_id.startswith("/"):
                    return static("images/placeholder.svg")
                options = dict(image.url_options, secure=True)
                url = image.build_url(**options)
                # A URL-shaped public_id can bypass SDK URL construction.
                # Only accept a credential-free HTTPS delivery URL here.
                parsed = urlsplit(url)
                if (
                    parsed.scheme != "https"
                    or not parsed.hostname
                    or parsed.username
                    or parsed.password
                ):
                    return static("images/placeholder.svg")
            else:
                url = image.url
        except (AttributeError, TypeError, ValueError):
            pass
        else:
            if url:
                return url
    return static("images/placeholder.svg")
