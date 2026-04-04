from django.apps import AppConfig


class PinterestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pinterest'

    def ready(self):
        import pinterest.signals  # noqa
