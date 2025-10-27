from django.http import HttpResponse
from django.conf import settings
import os

def robots_txt(request):
    path = os.path.join(settings.BASE_DIR, "static", "robots.txt")
    with open(path, "r") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    path = os.path.join(settings.BASE_DIR, "static", "sitemap.xml")
    with open(path, "r") as f:
        content = f.read()
    return HttpResponse(content, content_type="application/xml")
