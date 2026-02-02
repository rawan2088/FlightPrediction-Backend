from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'message': 'Flight Prediction API',
        'version': '1.0.0',
        'endpoints': {
            'users': {
                'register': '/api/users/register/ [POST]',
                'login': '/api/users/login/ [POST]',
                'refresh_token': '/api/users/token/refresh/ [POST]',
                'profile': '/api/users/profile/ [GET] (Auth required)',
                'update_profile': '/api/users/profile/update/ [PUT, PATCH] (Auth required)',
            },
            'predictions': {
                'history': '/api/predictions/history/ [GET] (Auth required)',
            }
        },    })