from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render

from game.generators import UserAttemptLogGenerator
from game.models import UserChanImageAttempt
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
            answer_result = game.process_answer(given_answer, int(image_id_to_guess))
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
        chan_image_id, chan_image_url, words_lengths, letters = None, None, None, None
        try:
            result = game.get_chan_image_result()
            chan_image_id = result.chan_image_id
            chan_image_url = result.chan_image_url
            words_lengths = result.words_lengths
            letters = result.letters
        except Exception as exc:
            message = exc
        image = {
            'id': chan_image_id,
            'url': chan_image_url,
            'words_lengths': words_lengths,
            'letters': letters,
            'message': message,
        }

    attrs = {
        'user': request.user,
        'form': UserLoginForm(request),
        'image': image,
        'answer_result': answer_result.__dict__ if answer_result else None,
    }
    return render(request, 'game/index.html', attrs)


@login_required
def logs(request):
    attempts = UserAttemptLogGenerator(request.user).get_user_attempt_logs()
    attrs = {
        'form': UserLoginForm(request),
        'attempts': attempts,
    }
    return render(request, 'game/logs.html', attrs)
