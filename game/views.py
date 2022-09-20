from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from verify_email import send_verification_email

from game.forms import UserLoginForm, UserSignupForm, UserProfileForm
from game.models import ChanImage, CharacterName, CharacterImage
from project.models import User


def get_next_chan_image_for_user(user):
    # TO DO: create user day's chans batch if don't exist, else pick first unsolved
    chan_image = ChanImage.objects.order_by('?').first()
    return chan_image


def get_answer_result(answer, chan_image_id):
    is_correct = False
    answered = CharacterName.objects.filter(name__iexact=answer).first()
    correct = ChanImage.objects.filter(id=chan_image_id).first()
    if answered and correct and answered.character == correct.chan.character:
        is_correct = True
    return {
        'correct': is_correct,
        'correct_answer': CharacterName.objects.filter(character=correct.chan.character, lang__alpha='en').first().name,
        'url': CharacterImage.objects.filter(character=correct.chan.character).first().image.url,
    }


def index(request):
    answer_result = None
    if request.method == 'POST':
        answer_result = get_answer_result(request.POST['answer'], request.POST['image_id'])
        image = {'id': 0, 'url': answer_result['url']}
    else:
        chan_image = get_next_chan_image_for_user(request.user)
        image = {'id': chan_image.id, 'url': chan_image.image.url}
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


def verify_info(request):
    return render(request, 'game/verify_info.html')


class SignUpView(generic.CreateView):
    form_class = UserSignupForm
    success_url = reverse_lazy("game:verify_info")
    template_name = "game/signup.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form(UserSignupForm)
        if form.is_valid():
            send_verification_email(request, form)
        return super(SignUpView, self).post(request, *args, **kwargs)


class ProfileView(generic.UpdateView):
    form_class = UserProfileForm
    success_url = reverse_lazy("game:profile")
    template_name = "game/profile.html"
    queryset = User.objects.all()

    def get_object(self, queryset=None):
        obj = self.queryset.get(pk=self.request.user.id)
        return obj
