from django.apps import AppConfig

class HotelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hotel'

    def ready(self):
        import hotel.signals  # Ensure signals.py is loaded
