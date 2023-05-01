from rest_framework import viewsets, permissions
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from api.serializers import AnswerResultSerializer, ChanImageResultSerializer, UserSerializer
from game.exceptions import BaseChanException
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
        if self.action == 'get_chan_image_result':
            return ChanImageResultSerializer
        if self.action == 'get_answer_result':
            return AnswerResultSerializer
        return ChanImageResultSerializer

    def get_chan_image_result(self, request):
        game = GameProcessor(user=request.user)
        chan_image_result = game.get_chan_image_result()
        serializer = self.get_serializer(chan_image_result)
        return Response(serializer.data)

    def get_answer_result(self, request):
        chan_image_id_to_guess = request.data.get('chan_image_id')
        if not chan_image_id_to_guess:
            raise APIException("Chan Image ID is not provided")
        given_answer = request.data.get('given_answer')
        need_to_show_correct_answer = request.data.get('need_to_show_correct_answer', False)

        try:
            game = GameProcessor(user=request.user, show_correct_answer=need_to_show_correct_answer)
            answer_result = game.process_answer(given_answer, int(chan_image_id_to_guess))
            serializer = self.get_serializer(data=answer_result.__dict__)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as exc:
            raise APIException(exc)
