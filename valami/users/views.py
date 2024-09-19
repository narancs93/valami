from .models import User
from .serializers import PublicUserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class UserRetrieveViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = [IsAuthenticated]
