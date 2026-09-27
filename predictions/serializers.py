from rest_framework import serializers
from .models import Prediction


class PredictionSerializer(serializers.ModelSerializer):
    airline_name = serializers.CharField(source='airline.name', read_only=True, default=None)
    requested_by = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Prediction
        fields = [
            'id',
            'flight_number',
            'airline',
            'airline_name',
            'origin',
            'destination',
            'scheduled_departure',
            'predicted_delay_minutes',
            'requested_by',
            'created_at',
        ]
        read_only_fields = fields


class PredictionRequestSerializer(serializers.Serializer):
    """
    What OUR api accepts from the frontend — plain snake_case, our own
    naming. This is deliberately decoupled from the ML model's training
    column names (ORIGIN_AIRPORT, SCHEDULED_TIME, etc.) so that a change
    on the ML side never forces a frontend change.
    """
    origin_airport = serializers.CharField(max_length=3)
    destination_airport = serializers.CharField(max_length=3)
    airline = serializers.CharField(max_length=3)
    year = serializers.IntegerField(min_value=2015, max_value=2035)
    month = serializers.IntegerField(min_value=1, max_value=12)
    day = serializers.IntegerField(min_value=1, max_value=31)
    day_of_week = serializers.IntegerField(min_value=0, max_value=6)
    departure_delay = serializers.IntegerField(default=0)
    scheduled_time_minutes = serializers.IntegerField(min_value=0, max_value=1439)
    distance = serializers.IntegerField(min_value=0)

    def to_ml_payload(self) -> dict:
        """Translate our clean field names into the shape the ML service expects."""
        data = self.validated_data
        return {
            "ORIGIN_AIRPORT": data["origin_airport"].upper(),
            "DESTINATION_AIRPORT": data["destination_airport"].upper(),
            "AIRLINE": data["airline"].upper(),
            "YEAR": data["year"],
            "MONTH": data["month"],
            "DAY": data["day"],
            "DAY_OF_WEEK": data["day_of_week"],
            "DEPARTURE_DELAY": data["departure_delay"],
            "SCHEDULED_TIME": data["scheduled_time_minutes"],
            "DISTANCE": data["distance"],
        }