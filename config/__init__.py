"""Django project init — export Celery app for shared_task binding."""
from .celery import app as celery_app

__all__ = ("celery_app",)
