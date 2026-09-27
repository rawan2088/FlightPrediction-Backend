from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.create_prediction, name='predict'),
    path('predict/warmup/', views.warmup_prediction_service, name='predict-warmup'),
    path('history/', views.prediction_history, name='prediction-history'),
    path('airline-stats/', views.airline_collective_results, name='airline-collective-results'),
]