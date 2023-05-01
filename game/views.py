from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render

from game.processors import GameProcessor
from project.forms import UserLoginForm


def index(request):
    user = request.user if not isinstance(request.user, AnonymousUser) else None
    answer_result, message = None, None
    show_correct_answer = request.POST.get('show_correct_answer', False)
    game = GameProcessor(user=user, show_correct_answer=show_correct_answer)

    # POST for guessing last pending Chan
    if request.method == 'POST':
        given_answer = request.POST['answer']
        image_id_to_guess = request.POST['image_id']
        try:
            answer_result = game.process_answer(given_answer, image_id_to_guess)
        except Exception as exc:
            message = exc
        image = {
            'id': request.POST['image_id'],
            'url': answer_result.character_image_url if answer_result and (
                answer_result.is_correct or game.show_correct_answer
            ) else None,
            'message': message,
        }
    # GET for getting next Chan
    else:
        chan_image_id, chan_image_url = None, None
        try:
            result = game.get_chan_image_result()
            chan_image_id = result.chan_image_id
            chan_image_url = result.chan_image_url
        except Exception as exc:
            message = exc
        image = {
            'id': chan_image_id,
            'url': chan_image_url,
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
