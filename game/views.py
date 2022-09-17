from django.shortcuts import render

from game.forms import UserLoginForm


def index(request):
    # tasks = Task.objects.all()
    attrs = {
        'user': request.user,
        'form': UserLoginForm(request),
    }
    return render(request, 'game/index.html', attrs)


def about(request):
    attrs = {
        'title': 'Страница про нас',
        'form': UserLoginForm(request),
    }
    return render(request, 'game/about.html', attrs)
