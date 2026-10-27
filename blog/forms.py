from django import forms
from django.core.exceptions import ValidationError

from .models import BlogPost

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB


class BlogPostForm(forms.ModelForm):
    image = forms.ImageField(
        required=False, help_text="JPG, PNG or WEBP, maximum 5 MB."
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
