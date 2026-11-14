"""Factory Boy factories for test data generation."""
import factory
from django.contrib.auth import get_user_model

from apps.incidents.models import Incident
from apps.services.models import Service


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    name = factory.Sequence(lambda n: f"service-{n}")
    kind = "docker"
    endpoint = "http://localhost:8080/health"


class IncidentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Incident

    title = factory.Sequence(lambda n: f"Incident {n}")
    description = "Auto-generated test incident"
    severity = "medium"
    status = "open"
    service = factory.SubFactory(ServiceFactory)
