from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from .media import image_url
from .models import BlogPost, Subscriber

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB


class ImageReference:
    """Only wrap the widget value; preserve the model's original form value."""

    def __init__(self, image):
        self.image = image
        self.url = image_url(image)

    def __str__(self):
        return str(self.image)


class CloudinaryImageInput(forms.ClearableFileInput):
    def is_initial(self, value):
        # Accessing CloudinaryResource.url can raise without a cloud name.
        return bool(value) and not isinstance(value, UploadedFile)

    def format_value(self, value):
        if self.is_initial(value):
            return ImageReference(value)


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        max_length=Subscriber._meta.get_field("email").max_length
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class BlogPostForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        help_text="JPG, PNG or WEBP, maximum 5 MB.",
        widget=CloudinaryImageInput,
    )

    class Meta:
        model = BlogPost
        fields = ["title", "content", "image"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter post title...",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Write your story here...",
                }
            ),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "content_type"):
            if (
                image.content_type not in ALLOWED_IMAGE_TYPES
                or image.image.format not in {"JPEG", "PNG", "WEBP"}
            ):
                raise ValidationError(
                    "Only JPG, PNG or WEBP images are allowed."
                )
            if image.size > MAX_UPLOAD_SIZE:
                raise ValidationError("Image size cannot exceed 5 MB.")
        return image
