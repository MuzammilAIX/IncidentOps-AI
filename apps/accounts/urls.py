from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.api_login, name="api-login"),
    path("logout/", views.api_logout, name="api-logout"),
    path("me/", views.api_me, name="api-me"),
]
