from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=150, unique=True)
    kind = models.CharField(max_length=64, default="docker")
    endpoint = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
