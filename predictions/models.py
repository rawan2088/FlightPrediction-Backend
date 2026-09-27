from django.conf import settings
from django.db import models
from users.models import Airline


class Prediction(models.Model):
    """
    One flight-delay prediction produced by the AI model.

    `user` is whoever requested the prediction (any authenticated user —
    normal or airline). `airline` identifies which airline's *flight* this
    prediction concerns — set from the flight number when the prediction
    is created, e.g. by looking up Airline.objects.get(iata_code=...) on
    the prefix of flight_number. This is deliberately independent of
    `user.airline`, since a normal user can look up a prediction for any
    airline's flight, and that's exactly what should count toward that
    airline's collective results.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictions',
    )
    airline = models.ForeignKey(
        Airline,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions',
    )

    flight_number = models.CharField(max_length=20)
    origin = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    scheduled_departure = models.DateTimeField()

    predicted_delay_minutes = models.FloatField()

    # Whatever raw features you fed the AI agent (weather, day of week,
    # aircraft type, etc.) — kept as JSON so you don't need a migration
    # every time the model's feature set changes.
    input_features = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['airline', '-created_at']),
        ]

    def __str__(self):
        return f"{self.flight_number} -> {self.predicted_delay_minutes:.0f} min ({self.user})"