from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        # Import signal handlers
        try:
            import reviews.signals  # noqa: F401
        except Exception:
            pass
