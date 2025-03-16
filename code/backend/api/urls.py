from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LLMModelViewSet, DatasetViewSet, QuestionViewSet, TestViewSet, QuestionResultViewSet
from .views.auth_views import CustomTokenObtainPairView, CustomTokenRefreshView,  is_authenticated, register, logout

router = DefaultRouter()
router.register(r'llm-models', LLMModelViewSet)
router.register(r'datasets', DatasetViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'tests', TestViewSet)
router.register(r'question-results', QuestionResultViewSet)

urlpatterns = [
                  path('auth/register/', register),
                  path('auth/login/', CustomTokenObtainPairView.as_view()),
                  path('auth/refresh/', CustomTokenRefreshView.as_view()),
                  path('auth/logout/', logout),
                  path('auth/authenticated/',  is_authenticated),
                  path('api-auth/', include('rest_framework.urls')),
              ] + router.urls
