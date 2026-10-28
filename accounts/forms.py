from django import forms

from .models import PetProfile


class PetProfileForm(forms.ModelForm):
    class Meta:
        model = PetProfile
        fields = ["name", "species", "care_focus", "notes"]
        labels = {
            "name": "Pet's name",
            "species": "Species",
            "care_focus": "Everyday care focus",
            "notes": "Everyday care notes",
        }
        help_texts = {
            "notes": (
                "Optional. Add preferences, routines or reminders "
                "(up to 500 characters)."
            )
        }
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select"
                if isinstance(field.widget, forms.Select)
                else "form-control"
            )
