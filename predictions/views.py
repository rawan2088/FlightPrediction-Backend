from datetime import datetime, timedelta, timezone as dt_timezone

import requests
from django.conf import settings
from django.db.models import Avg, Count, Max, Min
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from users.models import Airline
from users.permissions import IsAirlineUser
from .models import Prediction
from .serializers import PredictionSerializer, PredictionRequestSerializer
from .services import get_delay_prediction, PredictionServiceError


class PredictionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prediction_history(request):
    """
    A user's own past predictions, newest first. Works the same for
    normal users and airline-role users — this is always "my history".
    """
    predictions = Prediction.objects.filter(user=request.user)

    paginator = PredictionPagination()
    page = paginator.paginate_queryset(predictions, request)
    serializer = PredictionSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAirlineUser])
def airline_collective_results(request):
    """
    Airline-only: every prediction tagged with the requesting user's
    airline (regardless of who requested it), plus summary stats.

    IsAirlineUser (in users/permissions.py) already guarantees
    request.user.airline is set, so no null-check is needed here.
    """
    airline = request.user.airline
    predictions = Prediction.objects.filter(airline=airline)

    stats = predictions.aggregate(
        total_predictions=Count('id'),
        average_delay_minutes=Avg('predicted_delay_minutes'),
        max_delay_minutes=Max('predicted_delay_minutes'),
        min_delay_minutes=Min('predicted_delay_minutes'),
    )

    paginator = PredictionPagination()
    page = paginator.paginate_queryset(predictions, request)
    serializer = PredictionSerializer(page, many=True)
    paginated = paginator.get_paginated_response(serializer.data)

    return Response({
        'airline': airline.name,
        'stats': stats,
        **paginated.data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_prediction(request):
    """
    The endpoint the frontend now calls instead of hitting the ML service
    directly. Flow:
      1. validate the incoming form data
      2. translate it into the ML service's expected shape and call it
         (server-side — the ML host is never exposed to the browser)
      3. resolve/create the Airline row for this IATA code, so the
         prediction can be counted toward that airline's collective stats
      4. persist a Prediction row tied to request.user
      5. return the prediction to the frontend
    """
    request_serializer = PredictionRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    validated = request_serializer.validated_data
    ml_payload = request_serializer.to_ml_payload()

    try:
        delay_minutes = get_delay_prediction(ml_payload)
    except PredictionServiceError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    airline_code = validated['airline'].upper()
    airline, _ = Airline.objects.get_or_create(
        iata_code=airline_code,
        defaults={'name': airline_code},  # real name can be filled in later via admin
    )

    scheduled_departure = (
        datetime(validated['year'], validated['month'], validated['day'], tzinfo=dt_timezone.utc)
        + timedelta(minutes=validated['scheduled_time_minutes'])
    )

    # The form doesn't collect a real flight number, so we synthesize a
    # stable identifier from what we do have. Swap this out if/when the
    # frontend starts collecting an actual flight number.
    flight_number = f"{airline_code}-{validated['origin_airport'].upper()}{validated['destination_airport'].upper()}"

    prediction = Prediction.objects.create(
        user=request.user,
        airline=airline,
        flight_number=flight_number,
        origin=validated['origin_airport'].upper(),
        destination=validated['destination_airport'].upper(),
        scheduled_departure=scheduled_departure,
        predicted_delay_minutes=delay_minutes,
        input_features=ml_payload,
    )

    return Response(
        {
            'predicted_arrival_delay_minutes': delay_minutes,
            'prediction': PredictionSerializer(prediction).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def warmup_prediction_service(request):
    """
    Fire-and-forget ping to wake up the ML service if it's a sleeping
    Fly.io machine. Public on purpose — this should fire the moment the
    page loads, before the user has necessarily logged in, and it returns
    no prediction data, just triggers a wake-up. Any failure is swallowed:
    a failed warmup should never block the page.
    """
    try:
        requests.post(settings.ML_PREDICTION_API_URL, timeout=3)
    except requests.exceptions.RequestException:
        pass
    return Response(status=status.HTTP_204_NO_CONTENT)