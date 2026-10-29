from django.db import models
from cloudinary.models import CloudinaryField

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = CloudinaryField('image', blank=True, null=True)

    @property
    def image_is_ai_illustration(self):
        """Recognise the reserved owner-reviewed namespace, not image content."""
        from .catalogue import AI_IMAGE_PREFIX

        public_id = getattr(self.image, "public_id", "")
        return isinstance(public_id, str) and public_id.startswith(AI_IMAGE_PREFIX)

    def __str__(self):
        return self.name
