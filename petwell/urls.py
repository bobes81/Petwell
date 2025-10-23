"""
URL configuration for petwell project.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf.urls import handler404


# --- Robots.txt handler ---
def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Disallow:\n"
        "Sitemap: https://petwell-app-ivo-59ea39e413cf.herokuapp.com/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")


# --- Custom 404 handler ---
def custom_404(request, exception=None):
    return render(request, "404.html", status=404)


# --- URL patterns ---
urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("blog.urls")),
    path("accounts/", include("allauth.urls")),

    # Redirect homepage to blog
    path("", lambda request: redirect("blog_list")),

    # Serve robots.txt
    path("robots.txt", robots_txt, name="robots_txt"),
]

# --- Attach 404 handler ---
handler404 = custom_404