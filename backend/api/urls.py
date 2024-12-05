from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.main),
    path('ask_gpt/', views.ask_gpt),
    path('auth/register', views.register),
    path('auth/login', TokenObtainPairView.as_view()),
    path('auth/refresh', TokenRefreshView.as_view()),
    path('auth/logout/', views.logout),
    path('api-auth/', include('rest_framework.urls')),

]
