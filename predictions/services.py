import requests
from django.conf import settings


class PredictionServiceError(Exception):
    """Raised when the external ML prediction service can't be reached or errors out."""
    pass


def get_delay_prediction(ml_payload: dict) -> float:
    """
    Calls the external flight-delay ML service and returns the predicted
    arrival delay in minutes (negative = early).

    Kept in its own function rather than inline in the view so that:
    (1) the view stays easy to read and test, and
    (2) if the ML host, auth, or payload shape ever changes, there's
        exactly one place in the whole codebase to update.
    """
    try:
        response = requests.post(
            settings.ML_PREDICTION_API_URL,
            json=ml_payload,
            timeout=settings.ML_PREDICTION_API_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise PredictionServiceError("The prediction service timed out.")
    except requests.exceptions.RequestException as exc:
        raise PredictionServiceError(f"The prediction service failed: {exc}")

    data = response.json()
    if "predicted_arrival_delay_minutes" not in data:
        raise PredictionServiceError("Unexpected response shape from prediction service.")

    return data["predicted_arrival_delay_minutes"]