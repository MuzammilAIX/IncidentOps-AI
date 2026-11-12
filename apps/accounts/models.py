from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model — required because AUTH_USER_MODEL = "accounts.User".
    Must be defined BEFORE running `manage.py migrate`.
    """
    display_name = models.CharField(max_length=150, blank=True)
    timezone = models.CharField(max_length=64, default="UTC")

    def __str__(self):
        return self.username