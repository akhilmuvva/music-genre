from django.apps import AppConfig


class ClassifierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Register the app under the package name so Django can import it inside the container
    name = 'music_genre_classifier'
