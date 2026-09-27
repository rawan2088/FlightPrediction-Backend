from django.db import models
from django.contrib.auth.models import AbstractUser


class Airline(models.Model):
    """
    An airline company. Airline-role users belong to one of these, and
    Predictions are tagged with an airline so that airline accounts can
    pull every prediction that concerns their flights — not just the ones
    their own staff happened to request.
    """
    name = models.CharField(max_length=100, unique=True)
    iata_code = models.CharField(
        max_length=3,
        unique=True,
        help_text="2-3 letter IATA airline code, e.g. 'DL', 'AA', 'BA'",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.iata_code})"


class User(AbstractUser):
    class Role(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal User'
        AIRLINE_STAFF = 'AIRLINE_STAFF', 'Airline Staff'
        AIRLINE_ADMIN = 'AIRLINE_ADMIN', 'Airline Admin'

    # Email should be unique
    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.NORMAL,
    )

    # Only ever set for AIRLINE_STAFF / AIRLINE_ADMIN accounts.
    # Set via Django admin by a superuser — never through public
    # registration, to avoid a user granting themselves airline access.
    airline = models.ForeignKey(
        Airline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff',
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_airline_user(self):
        return self.role in (self.Role.AIRLINE_STAFF, self.Role.AIRLINE_ADMIN)

    # for debugging purposes
    def __str__(self):
        return self.email