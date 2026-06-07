from django.apps import AppConfig


class ImoveisConfig(AppConfig):
    name = 'apps.imoveis'

    def ready(self):
        import apps.imoveis.signals  # noqa: F401
