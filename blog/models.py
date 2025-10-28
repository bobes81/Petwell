from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = CloudinaryField('image', blank=True, null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """Safe delete to prevent Cloudinary errors when image no longer exists."""
        try:
            if self.image and hasattr(self.image, 'public_id') and self.image.public_id:
                self.image.delete()  # safely remove from Cloudinary
        except Exception as e:
            print(f"⚠️ Skipping Cloudinary delete error: {e}")
        super().delete(*args, **kwargs)