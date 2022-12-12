from django.contrib.auth.models import AnonymousUser
from django.db.models import F
from django.shortcuts import render

from common.utils import deep_getattr
from game.generators import ChanImageGenerator
from game.models import ChanImage, CharacterName, CharacterImage, UserChanImageAttempt
from guess_chan.settings import NORMAL_MODE
from project.forms import UserLoginForm
from project.models import User


def get_next_chan_image_for_user(user, mode=NORMAL_MODE):
    # TO DO: create user day's chans batch if don't exist, else pick first unsolved
    message = ''
    chan_image = None
    if getattr(user, 'energy', 1) > 0:
        chan_image = ChanImageGenerator(user, mode).get_next_chan_image()
        if not chan_image:
            message = 'Chan not found'
    else:
        message = 'Out of energy'
    return chan_image, message


def decrement_energy(user):
    user.energy -= 1
    user.save()


def get_answer_result(user, answer, chan_image_id):
    is_correct_answer = False
    answered = CharacterName.objects.filter(name__iexact=answer).first()
    correct = ChanImage.objects.filter(id=chan_image_id).first()
    chan_image_attempt = UserChanImageAttempt.objects.filter(
        user=user,
        chan_image_id=chan_image_id,
        is_pending=True,
    ).first()
    if chan_image_attempt:
        decrement_energy(user)
        if answered and correct and answered.character == correct.chan.character:
            chan_image_attempt.is_solved = True
            is_correct_answer = True
        chan_image_attempt.is_pending = False
        chan_image_attempt.save()
    return {
        'correct': is_correct_answer,
        'correct_answer': CharacterName.objects.filter(character=correct.chan.character, lang__alpha='en').first().name,
        'url': deep_getattr(CharacterImage.objects.filter(character=correct.chan.character).first(), 'image', 'url'),
    }


def index(request):
    user = request.user if not isinstance(request.user, AnonymousUser) else None
    answer_result = None
    if request.method == 'POST':
        answer_result = get_answer_result(user, request.POST['answer'], request.POST['image_id'])
        image = {'id': 0, 'url': answer_result['url'], 'error': ''}
    else:
        chan_image, message = get_next_chan_image_for_user(user)
        image = {
            'id': deep_getattr(chan_image, 'id'),
            'url': deep_getattr(chan_image, 'image', 'url'),
            'error': message,
        }
    attrs = {
        'user': request.user,
        'form': UserLoginForm(request),
        'image': image,
        'answer_result': answer_result,
    }
    return render(request, 'game/index.html', attrs)


def about(request):
    attrs = {
        'title': 'About us',
        'form': UserLoginForm(request),
    }
    return render(request, 'game/about.html', attrs)
