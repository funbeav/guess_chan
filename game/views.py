from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect

from game.generators import UserAttemptLogGenerator
from game.objects import AttemptAnswerResult, ChanAttemptResult
from game.processors import GameProcessor
from project.forms import UserLoginForm


def index(request):
    user = request.user if not isinstance(request.user, AnonymousUser) else None
    answer_result, message = AttemptAnswerResult(), None
    game = GameProcessor(user=user, need_to_show_correct=request.user.is_always_show_correct_answer if user else None)

    # POST for guessing last pending Chan
    if request.method == 'POST':
        given_answer = request.POST['answer']
        attempt_id = request.POST['attempt_id']
        try:
            answer_result = game.process_answer(given_answer, int(attempt_id))
        except Exception as exc:
            message = exc
        attempt = {
            'id': attempt_id,
            'image_url': answer_result.character_image_url if (
                answer_result.is_correct or game.need_to_show_correct
            ) else None,
            'message': message,
        }
    # GET for getting next Chan
    else:
        attempt_id, chan_image_url, words_lengths, letters = None, None, None, None
        try:
            attempt_result: ChanAttemptResult = game.get_attempt()
            attempt_id = attempt_result.attempt_id
            chan_image_url = attempt_result.chan_image_url
            words_lengths = attempt_result.words_lengths
            letters = attempt_result.letters
        except Exception as exc:
            message = exc
        attempt = {
            'id': attempt_id,
            'image_url': chan_image_url,
            'words_lengths': words_lengths,
            'letters': letters,
            'message': message,
        }

    attrs = {
        'user': request.user,
        'form': UserLoginForm(request),
        'attempt': attempt,
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


@login_required
def show_correct(request):
    if request.method == 'POST':
        game = GameProcessor(user=request.user)
        attempt_id = request.POST['attempt_id']
        shown_answer, message = AttemptAnswerResult(), None
        try:
            shown_answer = game.show_answer(attempt_id)
            if request.POST.get('is_always_show_correct_answer'):
                request.user.is_always_show_correct_answer = True
                request.user.save()
        except Exception as exc:
            message = exc

        if request.POST.get('source_view') == 'home':
            attrs = {
                'user': request.user,
                'form': UserLoginForm(request),
                'attempt': {
                    'id': attempt_id,
                    'image_url': shown_answer.character_image_url,
                    'message': message,
                },
                'answer_result': shown_answer.__dict__ if shown_answer else None,
            }
            return render(request, 'game/index.html', attrs)

    return redirect('game:logs')
