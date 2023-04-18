from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render

from common.utils import deep_getattr
from game.processors import GameProcessor
from project.forms import UserLoginForm


def index(request):
    user = request.user if not isinstance(request.user, AnonymousUser) else None
    answer_result = None
    show_correct_answer = request.POST.get('show_correct_answer', False)
    game = GameProcessor(user=user, show_correct_answer=show_correct_answer)
    if request.method == 'POST':
        given_answer = request.POST['answer']
        image_id_to_guess = request.POST['image_id']
        answer_result = game.process_answer(given_answer, image_id_to_guess)
        image = {
            'id': request.POST['image_id'],
            'url': answer_result.correct_answer.image_url if (
                answer_result.is_correct or game.show_correct_answer
            ) else None,
            'message': '',
        }
    else:
        chan_image, message = game.get_next_chan_image()
        image = {
            'id': deep_getattr(chan_image, 'id'),
            'url': deep_getattr(chan_image, 'image', 'url'),
            'message': message,
        }
    attrs = {
        'user': request.user,
        'form': UserLoginForm(request),
        'image': image,
        'answer_result': answer_result.__dict__ if answer_result else None,
    }
    return render(request, 'game/index.html', attrs)


def about(request):
    attrs = {
        'title': 'About us',
        'form': UserLoginForm(request),
    }
    return render(request, 'game/about.html', attrs)
