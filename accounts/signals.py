from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Welcome to PetWell 🐾',
            f'Hello {instance.username},\n\nThank you for joining PetWell! '
            'We’re so happy to have you here. You can now log in and start using your account.\n\n'
            'With love,\nThe PetWell Team 💙',
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=True,
        )
