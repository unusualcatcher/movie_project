from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


class CustomUser(AbstractUser):
    birthdate = models.DateField(null=True, blank=True)


class Genre(models.Model):
    # Storing genre ID and name
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Movie(models.Model):
    # Storing movie details
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, related_name='movies', on_delete=models.SET_NULL, null=True)
    thumbnail_link = models.CharField(max_length=255, blank=True, null=True)
    duration = models.IntegerField()  # Duration in minutes
    original_language = models.CharField(max_length=255)  # Language name
    dubbed_languages = models.JSONField()  # List of dubbed languages, can store multiple

    def __str__(self):
        return self.name


class Preferences(models.Model):
    # Storing user preferences
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    language = models.CharField(max_length=255)  # Preferred language
    genre = models.JSONField(default=dict)  # HashMap of genre ids with initial values as 0
    suggestions = models.JSONField()  # List of movie IDs for suggestions

    def __str__(self):
        return f"Preferences for {self.user.username}"