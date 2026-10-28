from django.conf import settings
from django.db import models


class PetProfile(models.Model):
    """An owner's private pet details and everyday care reminders."""

    class Species(models.TextChoices):
        DOG = "dog", "Dog"
        CAT = "cat", "Cat"
        OTHER = "other", "Other"

    class CareFocus(models.TextChoices):
        GENERAL = "general", "General routine"
        NUTRITION = "nutrition", "Food and treats"
        DENTAL = "dental", "Dental care planning"
        CALM = "calm", "Calm and rest"
        MOBILITY = "mobility", "Activity and rest"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pet_profiles",
    )
    name = models.CharField(max_length=80)
    species = models.CharField(max_length=10, choices=Species.choices)
    care_focus = models.CharField(
        max_length=12,
        choices=CareFocus.choices,
        default=CareFocus.GENERAL,
    )
    notes = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name

    @property
    def routine_reminder(self):
        reminders = {
            self.CareFocus.GENERAL: (
                "Plan a consistent daily rhythm for feeding, play and rest."
            ),
            self.CareFocus.NUTRITION: (
                "Record meal and treat times so household members can follow "
                "a consistent routine."
            ),
            self.CareFocus.DENTAL: (
                "Set a reminder to discuss everyday dental care with your "
                "veterinary team."
            ),
            self.CareFocus.CALM: (
                "Note the quiet spaces and predictable activities your pet "
                "enjoys."
            ),
            self.CareFocus.MOBILITY: (
                "Record favourite activities and rest breaks to discuss at "
                "your next veterinary visit."
            ),
        }
        return reminders[self.care_focus]
