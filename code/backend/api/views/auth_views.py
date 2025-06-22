from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ..serializers.user_serializer import UserRegistrationSerializer, UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']


            res = Response(
                {
                    "success": True,
                    "message": "Login successful.",
                }
            )

            res.set_cookie(
                key='access_token',
                value=str(access_token),
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            res.set_cookie(
                key='refresh_token',
                value=str(refresh_token),
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            return res

        except Exception as e:
            print(e)
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            if not refresh_token:
                return Response({'refreshed': False, 'error': 'No refresh token provided'}, status=status.HTTP_400_BAD_REQUEST)

            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens['access']
            refresh_token = tokens['refresh']

            res = Response(
                {
                    "success": True,
                    "message": "Token refreshed successfully.",
                }
            )

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            res.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            return res

        except Exception as e:
            print(e)
            return Response({'refreshed': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        return Response(
            {
                "success": True,
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"success": False, "error": "No refresh token found in cookies."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception:
            return Response({"success": False, "error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        res = Response({"success": True, "message": "Successfully logged out."}, status=status.HTTP_200_OK)

        res.delete_cookie("access_token", path='/', samesite='None')
        res.delete_cookie("refresh_token", path='/', samesite='None')

        return res

    except Exception as e:
        print(e)
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    user = request.user
    user_serializer = UserSerializer(user)

    return Response(
        {
            "success": True,
            "message": "User is authenticated.",
            "user": user_serializer.data
        },
        status=status.HTTP_200_OK
    )

