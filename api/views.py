from rest_framework import viewsets, permissions
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from api.serializers import AttemptAnswerResultSerializer, ChanAttemptResultSerializer, UserSerializer
from game.processors import GameProcessor
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


class GameViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'get_attempt':
            return ChanAttemptResultSerializer
        if self.action == 'get_answer_result':
            return AttemptAnswerResultSerializer
        return ChanAttemptResultSerializer

    def get_attempt(self, request):
        try:
            game = GameProcessor(user=request.user)
            chan_image_result = game.get_attempt()
            serializer = self.get_serializer(chan_image_result)
        except Exception as exc:
            raise APIException(exc)
        return Response(serializer.data)

    def get_answer_result(self, request):
        chan_image_id_to_guess = request.data.get('chan_image_id')
        if not chan_image_id_to_guess:
            raise APIException("Chan Image ID is not provided")
        given_answer = request.data.get('given_answer')
        need_to_show_correct = request.data.get('need_to_show_correct', False)

        try:
            game = GameProcessor(user=request.user, need_to_show_correct=need_to_show_correct)
            answer_result = game.process_answer(given_answer, int(chan_image_id_to_guess))
            serializer = self.get_serializer(answer_result, data=answer_result.__dict__)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as exc:
            raise APIException(exc)
