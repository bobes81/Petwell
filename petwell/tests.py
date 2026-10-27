from html.parser import HTMLParser
from urllib.parse import urlsplit
from xml.etree import ElementTree

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from blog.models import BlogPost


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href", "").startswith("/"):
            self.links.append(attrs["href"])
        if tag == "img" and attrs.get("src", "").startswith("/static/"):
            self.images.append(attrs["src"][8:])


class PublicPagesTests(TestCase):
    def test_pages_internal_links_and_local_images(self):
        author = get_user_model().objects.create_user("writer")
        post = BlogPost.objects.create(
            author=author, title="Story", content="Content"
        )
        pages = [
            "/",
            "/products/",
            "/blog/",
            reverse("blog:blog_detail", args=[post.pk]),
            "/cart/",
            "/checkout/",
            "/accounts/login/",
            "/accounts/signup/",
            "/accounts/password/reset/",
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)
                parser = Links()
                parser.feed(response.content.decode())
                for link in set(parser.links):
                    self.assertIn(
                        self.client.get(link).status_code, (200, 302), link
                    )
                for image in parser.images:
                    self.assertIsNotNone(finders.find(image), image)

    def test_seo_uses_render_domain_and_includes_blog(self):
        author = get_user_model().objects.create_user("writer")
        post = BlogPost.objects.create(
            author=author, title="Story", content="Content"
        )
        self.assertContains(
            self.client.get("/robots.txt"),
            "https://petwell-u0cr.onrender.com/sitemap.xml",
        )
        response = self.client.get("/sitemap.xml")
        root = ElementTree.fromstring(response.content)
        locations = [el.text for el in root.findall("{*}url/{*}loc")]
        self.assertIn(
            "https://petwell-u0cr.onrender.com"
            + reverse("blog:blog_detail", args=[post.pk]),
            locations,
        )
        self.assertTrue(
            all(
                urlsplit(url).netloc == "petwell-u0cr.onrender.com"
                for url in locations
            )
        )
        self.assertNotContains(response, "/checkout/")

    def test_unknown_url_uses_custom_404(self):
        self.assertEqual(self.client.get("/not-a-page/").status_code, 404)
