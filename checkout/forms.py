from django import forms


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100, label="Full name")
    # Match Order.email's database length before creating a PostgreSQL row.
    email = forms.EmailField(max_length=254)
    address = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Delivery address",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
