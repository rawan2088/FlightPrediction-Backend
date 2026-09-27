from django.contrib import admin
from django.urls import include, path

from flight_prediction.views import api_root

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/users/', include('users.urls')),
    path('api/predictions/', include('predictions.urls')),
]