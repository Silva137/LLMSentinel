from django.http import JsonResponse
from django.contrib import admin
from django.urls import path, include


def health(_): return JsonResponse({"status": "ok"})


def root(_request): return JsonResponse({"ok": True, "service": "llmsentinel-backend"})


urlpatterns = [
    path("", root),
    path("healthz", health),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
