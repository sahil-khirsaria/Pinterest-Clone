from django.apps import AppConfig


class UserAccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_account'

    def ready(self):
        import user_account.signals  # noqa
