from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .forms import BlogPostForm
from .models import BlogPost, Subscriber


class BlogTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(
            "author", email="author@example.test", password="TestPassword123!"
        )
        self.other = User.objects.create_user(
            "other", password="TestPassword123!"
        )
        self.staff = User.objects.create_user("staff", is_staff=True)
        self.post = BlogPost.objects.create(
            author=self.author,
            title="Original",
            content="Original content",
            image="sample",
        )
        self.edit = reverse("blog:edit_post", args=[self.post.pk])
        self.delete = reverse("blog:delete_post", args=[self.post.pk])

    def test_anonymous_users_cannot_create_edit_or_delete(self):
        for url in (reverse("blog:create_post"), self.edit, self.delete):
            self.assertEqual(self.client.get(url).status_code, 302)
            self.assertEqual(
                self.client.post(
                    url, {"title": "Attack", "content": "No"}
                ).status_code,
                302,
            )
        self.assertTrue(BlogPost.objects.filter(pk=self.post.pk).exists())

    def test_non_author_direct_get_and_post_forbidden(self):
        self.client.force_login(self.other)
        for url in (self.edit, self.delete):
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(
                self.client.post(
                    url, {"title": "Attack", "content": "No"}
                ).status_code,
                403,
            )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Original")

    def test_author_can_edit_existing_cloudinary_image_without_upload(self):
        self.client.force_login(self.author)
        self.assertEqual(self.client.get(self.edit).status_code, 200)
        with patch("cloudinary.uploader.upload_resource") as upload:
            response = self.client.post(
                self.edit, {"title": "Edited", "content": "New content"}
            )
        self.assertRedirects(
            response, reverse("blog:blog_detail", args=[self.post.pk])
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Edited")
        self.assertTrue(self.post.image)
        upload.assert_not_called()

    def test_author_can_clear_image(self):
        self.client.force_login(self.author)
        response = self.client.post(
            self.edit,
            {"title": "Edited", "content": "New", "image-clear": "on"},
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertFalse(self.post.image)

    def test_create_sets_author_from_authenticated_user(self):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("blog:create_post"),
            {"title": "Created", "content": "Story", "author": self.other.pk},
        )
        self.assertRedirects(response, reverse("blog:blog_list"))
        self.assertEqual(
            BlogPost.objects.get(title="Created").author, self.author
        )

    def test_staff_can_edit_and_delete_another_authors_post(self):
        self.client.force_login(self.staff)
        self.assertEqual(
            self.client.post(
                self.edit, {"title": "Moderated", "content": "Content"}
            ).status_code,
            302,
        )
        self.assertEqual(self.client.get(self.delete).status_code, 200)
        self.assertEqual(self.client.post(self.delete).status_code, 302)
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())

    def test_get_delete_only_confirms_author_post_deletes(self):
        self.client.force_login(self.author)
        self.assertContains(
            self.client.get(self.delete), reverse("blog:blog_list")
        )
        self.assertTrue(BlogPost.objects.filter(pk=self.post.pk).exists())
        self.assertRedirects(
            self.client.post(self.delete), reverse("blog:blog_list")
        )
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())

    def test_invalid_edit_does_not_overwrite_post(self):
        self.client.force_login(self.author)
        self.assertEqual(
            self.client.post(
                self.edit, {"title": "", "content": ""}
            ).status_code,
            200,
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Original")

    def image(self, name="image.png", content_type="image/png"):
        data = BytesIO()
        Image.new("RGB", (8, 8), "green").save(data, format="PNG")
        return SimpleUploadedFile(
            name, data.getvalue(), content_type=content_type
        )

    def test_valid_new_image_accepted(self):
        form = BlogPostForm(
            {"title": "Image", "content": "Content"}, {"image": self.image()}
        )
        self.assertTrue(form.is_valid(), form.errors)

    def gif_image(self):
        data = BytesIO()
        Image.new("RGB", (8, 8), "green").save(data, format="GIF")
        return SimpleUploadedFile(
            "spoofed.png", data.getvalue(), content_type="image/png"
        )

    def test_non_image_and_disallowed_format_rejected(self):
        for upload in (
            SimpleUploadedFile(
                "fake.png", b"not an image", content_type="image/png"
            ),
            self.gif_image(),
        ):
            form = BlogPostForm(
                {"title": "Image", "content": "Content"}, {"image": upload}
            )
            self.assertFalse(form.is_valid())
            self.assertIn("image", form.errors)

    def test_oversized_valid_image_rejected(self):
        upload = self.image()
        upload.size = 5 * 1024 * 1024 + 1
        form = BlogPostForm(
            {"title": "Image", "content": "Content"}, {"image": upload}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Image size", str(form.errors))

    def test_newsletter_validation_and_duplicates(self):
        url = reverse("blog:subscribe")
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url, {"email": "invalid"})
        self.assertFalse(Subscriber.objects.exists())
        self.client.post(url, {"email": "Reader@Example.Test"})
        self.client.post(url, {"email": "reader@example.test"})
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_valid_image_upload_saved_through_cloudinary_adapter(self):
        from cloudinary import CloudinaryResource

        self.client.force_login(self.author)
        with patch(
            "cloudinary.uploader.upload_resource",
            return_value=CloudinaryResource(
                public_id="new-image", format="png", resource_type="image"
            ),
        ) as upload:
            response = self.client.post(
                self.edit,
                {
                    "title": "With image",
                    "content": "Story",
                    "image": self.image(),
                },
            )
        self.assertEqual(response.status_code, 302)
        upload.assert_called_once()
        self.post.refresh_from_db()
        self.assertEqual(self.post.image.public_id, "new-image")

    def test_failed_image_upload_shows_validation_error_without_overwrite(
        self,
    ):
        from cloudinary.exceptions import Error

        self.client.force_login(self.author)
        with patch(
            "cloudinary.uploader.upload_resource", side_effect=Error("offline")
        ):
            response = self.client.post(
                self.edit,
                {
                    "title": "Not saved",
                    "content": "Story",
                    "image": self.image(),
                },
            )
        self.assertContains(response, "Image upload is unavailable")
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Original")

    def test_missing_cloud_name_uses_placeholder_on_shop_and_blog(self):
        import cloudinary

        from products.models import Product

        Product.objects.create(
            name="Stored product", price="7.25", image="stored-product-image"
        )
        pages = (
            reverse("blog:blog_list"),
            reverse("blog:blog_detail", args=[self.post.pk]),
            reverse("products:product_list"),
        )
        with patch.object(cloudinary.config(), "cloud_name", None):
            for page in pages:
                with self.subTest(page=page):
                    self.assertContains(
                        self.client.get(page), "/static/images/placeholder.svg"
                    )

    def test_author_can_edit_retained_image_without_cloud_name(self):
        import cloudinary

        self.client.force_login(self.author)
        with patch.object(cloudinary.config(), "cloud_name", None):
            with patch("cloudinary.uploader.upload_resource") as upload:
                response = self.client.get(self.edit)
                self.assertContains(response, "image-clear")
                self.assertContains(response, "/static/images/placeholder.svg")
                response = self.client.post(
                    self.edit,
                    {"title": "Text edit", "content": "Retain stored image"},
                )
                self.assertRedirects(
                    response,
                    reverse("blog:blog_detail", args=[self.post.pk]),
                )
            upload.assert_not_called()
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Text edit")
        self.assertEqual(self.post.image.public_id, "sample")

    def test_author_can_clear_image_without_cloud_name(self):
        import cloudinary

        self.client.force_login(self.author)
        with patch.object(cloudinary.config(), "cloud_name", None):
            response = self.client.post(
                self.edit,
                {"title": "No image", "content": "Text", "image-clear": "on"},
            )
            self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertFalse(self.post.image)

    def test_newsletter_rejects_valid_email_exceeding_database_length(self):
        from django.core.validators import validate_email

        email = (
            "a" * 64 + "@" + ".".join(["b" * 63, "c" * 63, "d" * 63, "e" * 60])
        )
        validate_email(email)
        self.assertGreater(len(email), 254)
        self.assertRedirects(
            self.client.post(reverse("blog:subscribe"), {"email": email}),
            reverse("home"),
        )
        self.assertFalse(Subscriber.objects.exists())
