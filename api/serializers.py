from rest_framework import serializers

from project.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'login', 'email', 'date_created']


class ChanImageResultSerializer(serializers.Serializer):
    chan_image_id = serializers.IntegerField()
    chan_image_url = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=200)


class AnswerResultSerializer(serializers.Serializer):
    chan_image_id = serializers.IntegerField(required=True, allow_null=False)
    given_answer = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=200)
    need_to_show_correct_answer = serializers.BooleanField(required=False, write_only=True)

    is_correct = serializers.BooleanField(read_only=True, default=False)
    correct_answer = serializers.CharField(read_only=True, default=None, max_length=200)
    character_image_url = serializers.CharField(read_only=True, default=None, max_length=200)
