from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LLMModelViewSet, DatasetViewSet, QuestionViewSet, TestViewSet, QuestionResultViewSet, register, logout

router = DefaultRouter()
router.register(r'llm-models', LLMModelViewSet)
router.register(r'datasets', DatasetViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'tests', TestViewSet)
router.register(r'question-results', QuestionResultViewSet)

urlpatterns = [
                  path('auth/register/', register),
                  path('auth/login/', TokenObtainPairView.as_view()),
                  path('auth/refresh/', TokenRefreshView.as_view()),
                  path('auth/logout/', logout),
                  path('api-auth/', include('rest_framework.urls')),
              ] + router.urls
