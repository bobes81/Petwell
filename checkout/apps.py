from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checkout"

    def ready(self):
        import stripe

        # Keep API calls well within the checkout lease and worker timeout.
        stripe.default_http_client = stripe.RequestsClient(timeout=10)
        stripe.max_network_retries = 0
