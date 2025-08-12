from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import UserAPIKey
from ..serializers.user_serializer import UserAPIKeySerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_api_key(request):
    # substitui se já existir
    UserAPIKey.objects.filter(user=request.user).delete()
    ser = UserAPIKeySerializer(data=request.data, context={"request": request})
    ser.is_valid(raise_exception=True)
    obj = ser.save()
    return Response({"success": True, "last4": obj.key_last4}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_api_key_info(request):
    try:
        obj = request.user.api_key
    except UserAPIKey.DoesNotExist:
        return Response({"has_key": False})
    return Response({"has_key": True, "last4": obj.key_last4})
