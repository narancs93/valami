from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserRetrieveViewSet

router = DefaultRouter()
router.register(r"users", UserRetrieveViewSet, basename="users_api")

urlpatterns = [
    path("api/", include(router.urls)),
]
