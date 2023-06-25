import random

from datetime import timedelta
from typing import Optional

from django.db.models import Subquery, Q
from django.utils import timezone

from game.constants import NORMAL_MODE, DEFAULT_LANG
from game.models import Chan, ChanImage, UserChanImageAttempt, CharacterName
from game.objects import WordsLettersResult
from project.models import User, Lang


class ChanImageGenerator:
    """Generates Chan Batches for current user"""

    def __init__(self, user: User, mode=NORMAL_MODE):
        self.user = user
        self.mode = mode
        self.chan_image = None

    def get_chan_name_by_chan_image(self, alpha2: str = None) -> str:
        """Get Chan name by Chan Image with alpha2 lang"""
        if not self.chan_image:
            return ''

        alpha2 = alpha2 or getattr(self.user, 'lang', None) or DEFAULT_LANG
        lang = Lang.objects.filter(alpha2=alpha2).first()
        if not lang:
            return ''

        character_name = CharacterName.objects.filter(
            character__chan=self.chan_image.chan,
            lang=lang,
        ).first()

        return character_name.name if character_name else ''

    def get_next_chan_image(self) -> Optional[ChanImage]:
        if not self.chan_image:
            self.chan_image = self._get_chan_image()
        return self.chan_image

    def _get_chan_image(self) -> Optional[ChanImage]:
        """Get chan image from UserChanImageAttempt"""
        # TO DO: cache already gotten self.chan_images
        result_chan_image = None

        # Get pending chan image
        if pending_chan_attempt := UserChanImageAttempt.objects.filter(
            user=self.user,
            mode=self.mode,
            is_pending=True,
            is_shown=False,
        ).last():
            result_chan_image = pending_chan_attempt.chan_image

        # Get chan image from previous attempt (with 10% chance)
        if not result_chan_image and self._is_lucky_to_show_previous_attempt():
            yesterday = timezone.localtime(timezone.now()) - timedelta(days=1)
            result_chan_image = self._get_chan_image_from_unsolved(created_lte=yesterday)

        # Create new attempt
        if not result_chan_image:
            showed_chans_ids = UserChanImageAttempt.objects.filter(
                user=self.user,
                mode=self.mode,
            ).values_list('chan__id', flat=True)
            new_chan = Chan.objects.filter(
                ~Q(id__in=showed_chans_ids),
            ).order_by('?').first()
            if new_chan:
                result_chan_image = ChanImage.objects.filter(chan=new_chan).order_by('?').first()
                UserChanImageAttempt.objects.create(
                    user=self.user,
                    mode=self.mode,
                    chan=new_chan,
                    chan_image=result_chan_image,
                )

        # Get chan image from previous attempts if out of chans
        if not result_chan_image:
            result_chan_image = self._get_chan_image_from_unsolved(
                created_lte=timezone.localtime(timezone.now()),
            )

        return result_chan_image

    @staticmethod
    def _is_lucky_to_show_previous_attempt() -> bool:
        return random.randint(1, 10) == 1   # 10% chance

    def _get_chan_image_from_unsolved(self, created_lte) -> Optional[ChanImage]:
        """Get unsolved chans from the past (<= created_lte)"""

        unsolved_attempt = UserChanImageAttempt.objects.filter(
            user=self.user,
            mode=self.mode,
            is_solved=False,
            created__lte=created_lte,
        ).exclude(
            chan_id__in=Subquery(
                UserChanImageAttempt.objects.filter(
                    user=self.user,
                    mode=self.mode,
                    is_shown=True,
                ).values_list('chan_id', flat=True),
            ),
        ).order_by('?').first()

        if unsolved_attempt:
            # Clone previous unsolved attempt to new attempt
            unsolved_attempt.pk = None
            unsolved_attempt.is_pending = True

            # Get one of the suitable chan images if there are several
            chan_image = ChanImage.objects.filter(
                chan=unsolved_attempt.chan,
            ).order_by('?').first()

            unsolved_attempt.chan_image = chan_image
            unsolved_attempt.save()

            return chan_image

        return None


class ShuffledWordsLettersGenerator:
    """Class for generating letters shuffled with random letters"""

    _LANG_LETTERS = {
        'en': {'vowels': 'AEIOU', 'consonants': 'BCDFGHJKLMNPQRSTVWXYZ'},
        'ru': {'vowels': 'АЕИОУЫЭЮЯ', 'consonants': 'БВГДЖЗЙКЛМНПРСТФХЦЧШЩ'},
        'de': {'vowels': 'AEIOUÄÖÜ', 'consonants': 'BCDFGHJKLMNPQRSTVWXYZß'},
    }

    def __init__(self, lang: str):
        self.lang = lang or 'en'    # by default lang = en

    def get_result_letters(self, source_string: str):
        words_lengths = [len(word) for word in source_string.strip().split(' ')]
        result_letters = [ch for ch in list(source_string.upper()) if ch.strip()]
        result_letters = self._add_random_letters_with_same_lang(result_letters)
        random.shuffle(result_letters)
        return WordsLettersResult(
            words_lengths=words_lengths,
            letters=result_letters,
        )

    def _add_random_letters_with_same_lang(self, letters: list[str]):
        """Method to add random letters with same lang.
        Should add n = len(letters) random letters with n/2 vowels and n/2 consonants"""

        vowels = self._LANG_LETTERS.get(self.lang).get('vowels')
        consonants = self._LANG_LETTERS.get(self.lang).get('consonants')

        num_letters = len(letters)
        num_vowels = num_letters // 2
        num_consonants = num_letters // 2

        result_letters = []

        # Add random vowels
        for _ in range(num_vowels):
            random_vowel = random.choice(vowels)
            result_letters.append(random_vowel)

        # Add random consonants
        for _ in range(num_consonants):
            random_consonant = random.choice(consonants)
            result_letters.append(random_consonant)

        result_letters.extend(letters)

        return result_letters
