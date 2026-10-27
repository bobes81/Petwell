"""Render stored images safely when optional Cloudinary settings are absent."""

from django.templatetags.static import static


def image_url(image):
    if image:
        try:
            url = image.url
        except (AttributeError, TypeError, ValueError):
            pass
        else:
            if url:
                return url
    return static("images/placeholder.svg")
