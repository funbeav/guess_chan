import imagehash
from PIL import Image
from django.db import models
from django.utils import timezone

from common.utils import generate_filename
from game.constants import DIFFICULTY_MODES, NORMAL_MODE
from project.models import Lang, User


class BaseImage(models.Model):
    image = models.ImageField(upload_to=generate_filename)
    caption = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=50, blank=True, default='Unknown')
    hash = models.CharField(max_length=20, blank=True, unique=False)

    def save(self, *args, **kwargs):
        self.hash = str(imagehash.average_hash(Image.open(getattr(self.image, 'file'))))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.caption or self.hash


class Character(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'[{self.pk}] {self.name}'


class CharacterImage(BaseImage):
    character = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def image_folder(self):
        return 'character'

    def __str__(self):
        return f'[{self.pk}] {self.character.name} Image'


class CharacterName(models.Model):
    """Acceptable Character's name"""

    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.character.name} ~ {self.name} ({self.lang.alpha2})'

    class Meta:
        unique_together = ('character', 'name')


class Chan(models.Model):
    character = models.OneToOneField(Character, on_delete=models.CASCADE, null=True, blank=True, related_name='chan')

    def __str__(self):
        return f'[{self.pk}] {self.character.name} Chan'


class ChanImage(BaseImage):
    chan = models.ForeignKey(Chan, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def image_folder(self):
        return 'chan'

    def __str__(self):
        return f'{self.chan} Image'


class UserChanImageAttempt(models.Model):
    """
    Model for storing all data about attempt of guessing chan_image by user
    guess_hints = {
        'en': {
            'shown_letters': ['s', 'i', 'a', 'k', 'c', 's', 'k'],
            'words_length': [4, 3],
            'correct_answer': 'Kick Ass',
        },
        'ru': {
            'shown_letters': ['е', 'и', 'п', 'п', 'ц'],
            'words_length': [5],
            'correct_answer': 'Пипец',
        },
    }
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    chan_image = models.ForeignKey(ChanImage, on_delete=models.CASCADE)

    created = models.DateTimeField(default=timezone.now)
    mode = models.CharField(max_length=6, choices=DIFFICULTY_MODES, default=NORMAL_MODE)

    is_solved = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    is_shown = models.BooleanField(default=False)

    given_answer = models.CharField(max_length=32, default='')
    guess_hints = models.JSONField()
    answer_lang = models.ForeignKey(Lang, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, commit: bool = True, *args, **kwargs):
        if commit:
            super().save(*args, **kwargs)

    def get_shown_letters(self, alpha2: str) -> []:
        return self.guess_hints.get(alpha2, {}).get('shown_letters', [])

    def get_words_lengths(self, alpha2: str) -> []:
        return self.guess_hints.get(alpha2, {}).get('words_lengths', [])

    def get_correct_answer(self, alpha2: str) -> []:
        return self.guess_hints.get(alpha2, {}).get('correct_answer', '')
