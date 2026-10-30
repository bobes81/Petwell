from html.parser import HTMLParser
from urllib.parse import urlsplit
from xml.etree import ElementTree

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import resolve, reverse

from blog.models import BlogPost
from products.models import Product


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.image_sources = []
        self.forms = []
        self.canonicals = []
        self.meta = {}
        self.h1_count = 0
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and attrs.get("name"):
            self.meta[attrs["name"]] = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href", ""))
        if tag == "form":
            self.forms.append(attrs)
        if tag == "img":
            self.image_sources.append(attrs.get("src", ""))
        if tag == "a" and attrs.get("href", "").startswith("/"):
            self.links.append(attrs["href"])
        if tag == "img" and attrs.get("src", "").startswith("/static/"):
            self.images.append(attrs["src"][8:])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


class PublicPagesTests(TestCase):
    def test_pages_internal_links_and_local_images(self):
        author = get_user_model().objects.create_user("writer")
        post = BlogPost.objects.create(
            author=author, title="Story", content="Content"
        )
        product = Product.objects.create(
            name="Paw balm", description="Gentle care", price="7.25"
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
                for form in parser.forms:
                    target = form.get("action") or page
                    resolve(urlsplit(target).path)
        shop = self.client.get(reverse("products:product_list"))
        parser = Links()
        parser.feed(shop.content.decode())
        action = reverse("cart:add_to_cart", args=[product.pk])
        self.assertIn({"method": "post", "action": action}, parser.forms)
        self.assertIn("/static/images/placeholder.svg", parser.image_sources)
        self.assertContains(shop, 'name="csrfmiddlewaretoken"')
        self.assertEqual(self.client.post(action).status_code, 302)
        self.assertContains(
            self.client.get(reverse("cart:view_cart")), product.name
        )

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


class SeoMetadataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user("seo-writer")
        cls.post = BlogPost.objects.create(
            author=cls.author,
            title='A pet story & "care"',
            content="Gentle care for pets & their people.",
        )
        cls.product = Product.objects.create(
            name="Paw balm", description="Gentle care", price="7.25"
        )

    def parsed(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        parser = Links()
        parser.feed(response.content.decode())
        return response, parser

    def test_public_metadata_is_distinct_with_one_main_heading(self):
        paths = [
            "/",
            "/products/",
            "/blog/",
            reverse("blog:blog_detail", args=[self.post.pk]),
        ]
        titles = set()
        descriptions = set()
        for path in paths:
            with self.subTest(path=path):
                _, page = self.parsed(path + "?utm_source=example")
                titles.add(page.title)
                descriptions.add(page.meta["description"])
                self.assertEqual(page.h1_count, 1)
                self.assertEqual(
                    page.canonicals,
                    ["https://petwell-u0cr.onrender.com" + path],
                )
                self.assertNotIn("noindex", page.meta.get("robots", ""))
        self.assertEqual(len(titles), len(paths))
        self.assertEqual(len(descriptions), len(paths))

    @override_settings(SITE_URL="https://configured.example/")
    def test_canonical_uses_configured_domain_without_query_string(self):
        _, page = self.parsed(
            "/products/?q=%22unexpected%22&utm_source=example"
        )
        self.assertEqual(
            page.canonicals, ["https://configured.example/products/"]
        )
        self.assertNotIn("testserver", page.canonicals[0])

    def test_private_pages_have_noindex_and_no_public_canonical(self):
        for path in [
            "/cart/",
            "/checkout/",
            "/accounts/login/",
            "/accounts/signup/",
            "/accounts/password/reset/",
        ]:
            with self.subTest(path=path):
                _, page = self.parsed(path)
                self.assertEqual(page.canonicals, [])
                self.assertIn("noindex", page.meta["robots"])
        self.client.force_login(self.author)
        for path in [
            "/orders/",
            "/blog/new/",
            "/accounts/logout/",
            reverse("blog:edit_post", args=[self.post.pk]),
            reverse("blog:delete_post", args=[self.post.pk]),
        ]:
            with self.subTest(path=path):
                _, page = self.parsed(path)
                self.assertEqual(page.canonicals, [])
                self.assertIn("noindex", page.meta["robots"])

    def test_blog_metadata_escapes_user_text_and_strips_description_markup(
        self,
    ):
        self.post.title = '<script>alert("title")</script> & pets'
        self.post.content = '<p>Gentle care & "tips" for pets.</p>'
        self.post.save()
        response, page = self.parsed(
            reverse("blog:blog_detail", args=[self.post.pk])
        )
        self.assertEqual(page.title, self.post.title + " | PetWell Blog")
        self.assertEqual(
            page.meta["description"], 'Gentle care & "tips" for pets.'
        )
        self.assertNotContains(response, '<script>alert("title")</script>')
        self.assertContains(response, "&lt;script&gt;")
        self.assertContains(response, "&quot;tips&quot;")
        self.assertEqual(page.h1_count, 1)

    def test_stored_product_image_without_cloud_name_has_local_fallback(self):
        import cloudinary

        Product.objects.filter(pk=self.product.pk).update(image="old-image")
        previous_name = cloudinary.config().cloud_name
        try:
            cloudinary.config(cloud_name=None)
            response, page = self.parsed("/products/")
        finally:
            cloudinary.config(cloud_name=previous_name)
        self.assertIn("/static/images/placeholder.svg", page.image_sources)
        self.assertContains(response, self.product.name)
        self.assertEqual(page.h1_count, 1)
        self.assertContains(response, "this.onerror=null")

    def test_authenticated_navbar_does_not_show_an_empty_timestamp(self):
        self.client.force_login(self.author)
        response, _ = self.parsed("/")
        self.assertContains(response, "Logged in as")
        self.assertNotContains(response, "<strong>seo-writer</strong> |")


class Outline(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.in_body = False
        self.body_styles = 0

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        if tag == "style" and self.in_body:
            self.body_styles += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False


class MarkupRegressionTests(TestCase):
    def test_pages_have_complete_outline_and_styles_outside_body(self):
        author = get_user_model().objects.create_user("outline-author")
        post = BlogPost.objects.create(
            author=author,
            title="Outline fixture",
            content="Local test content",
        )
        pages = [
            ("/", False),
            ("/products/", False),
            ("/blog/", False),
            ("/cart/", False),
            ("/checkout/", False),
            ("/accounts/login/", False),
            ("/accounts/signup/", False),
            ("/accounts/password/reset/", False),
            ("/pets/", True),
            ("/pets/new/", True),
            ("/blog/new/", True),
            (reverse("blog:edit_post", args=[post.pk]), True),
            (reverse("blog:delete_post", args=[post.pk]), True),
        ]
        for path, authenticated in pages:
            with self.subTest(path=path):
                self.client.logout()
                if authenticated:
                    self.client.force_login(author)
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                outline = Outline()
                outline.feed(response.content.decode())
                self.assertEqual(outline.headings.count(1), 1)
                self.assertEqual(outline.body_styles, 0)
                for previous, current in zip(
                    outline.headings, outline.headings[1:]
                ):
                    self.assertLessEqual(current, previous + 1)
