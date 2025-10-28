from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = CloudinaryField('image', blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Safe save override — prevents Cloudinary errors when image is unchanged.
        """
        if self.pk:
            old_post = BlogPost.objects.filter(pk=self.pk).first()
            if old_post and not self.image:
                self.image = old_post.image
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Safe delete override that prevents Cloudinary errors
        even if the image no longer exists or Cloudinary connection fails.
        """
        try:
            if self.image and hasattr(self.image, 'public_id'):
                public_id = getattr(self.image, 'public_id', None)
                if public_id:
                    try:
                        self.image.delete()  # attempt Cloudinary removal
                    except Exception as inner_error:
                        print(f"⚠️ Cloudinary image delete skipped: {inner_error}")
        except Exception as outer_error:
            print(f"⚠️ BlogPost delete error handled safely: {outer_error}")
        super().delete(*args, **kwargs)
# --- Newsletter Subscription Model ---
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
