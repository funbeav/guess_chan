from rest_framework import serializers

from project.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'login', 'email', 'date_created']
