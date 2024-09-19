from rest_framework import serializers
from .models import User


class PublicUserSerializer(serializers.ModelSerializer):
    """Serializer for public user data"""

    class Meta:
        model = User
        fields = ("id", "username", "name")
