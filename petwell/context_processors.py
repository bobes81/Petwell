"""SEO metadata for the site's public reading and shopping pages."""

from django.conf import settings

PUBLIC_PAGES = {
    ("", "home"),
    ("products", "product_list"),
    ("blog", "blog_list"),
    ("blog", "blog_detail"),
}


def seo_metadata(request):
    match = request.resolver_match
    public = bool(match and (match.namespace, match.url_name) in PUBLIC_PAGES)
    return {
        "seo_indexable": public,
        # SITE_URL is trusted configuration; never derive canonicals from Host.
        # request.path excludes search/query parameters and tracking identifiers.
        "seo_canonical_url": (
            settings.SITE_URL.rstrip("/") + request.path if public else ""
        ),
    }
