from rest_framework import viewsets, permissions

from api.serializers import UserSerializer
from project.models import User


class UserListViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        obj = self.queryset.get(pk=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj
