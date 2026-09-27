from django.contrib import admin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline', 'user', 'predicted_delay_minutes', 'created_at')
    list_filter = ('airline',)
    search_fields = ('flight_number', 'user__email')