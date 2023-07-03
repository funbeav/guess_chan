import random

from datetime import timedelta
from functools import cached_property
from typing import Optional

from django.db.models import Subquery, Q
from django.utils import timezone

from common.utils import deep_getattr
from game.constants import NORMAL_MODE, DEFAULT_LANG
from game.models import Chan, ChanImage, UserChanImageAttempt, CharacterName
from game.objects import WordsLettersResult, ChanAttemptResult, UserAttemptLog
from project.models import User, Lang


class ChanAttemptGenerator:
    """Generates Chan Batches for current user"""

    def __init__(self, user: User, mode=NORMAL_MODE):
        self.user = user
        self.mode = mode
        self.chan_attempt: Optional[UserChanImageAttempt] = None

    @cached_property
    def lang(self) -> Lang:
        """Return lang for user or default"""
        return getattr(self.user, 'lang', None) or Lang.objects.get(alpha2=DEFAULT_LANG)

    def _get_words_letters_result(self, string: str) -> WordsLettersResult:
        return ShuffledWordsLettersGenerator(
            self.lang.alpha2,
        ).get_result_letters(string)

    def _get_chan_name_by_chan_image(self, chan_image: ChanImage = None) -> str:
        """Get Chan name by Chan Image with alpha2 lang"""
        if not (chan_image and self.lang):
            return ''

        chan_name = CharacterName.objects.filter(
            character__chan=chan_image.chan,
            lang=self.lang,
        ).order_by('?').first()

        return chan_name.name if chan_name else ''

    def _check_and_update_chan_guess_hints_for_lang(self, chan_image: ChanImage):
        """If lang has changed - update it for new language in JSON fields"""
        if not (self.lang and self.chan_attempt):
            return

        if self.lang.alpha2 not in self.chan_attempt.guess_hints:
            chan_name = self._get_chan_name_by_chan_image(chan_image)
            words_letters_result = self._get_words_letters_result(chan_name)
            self.chan_attempt.guess_hints[self.lang.alpha2] = {
                'shown_letters': words_letters_result.letters,
                'words_lengths': words_letters_result.words_lengths,
                'correct_answer': chan_name,
            }
            self.chan_attempt.save()

    def get_next_chan_attempt(self) -> Optional[ChanAttemptResult]:
        """Get next ChanAttemptResult"""
        chan_image = self._get_chan_image()

        if not chan_image:
            return None

        if self.chan_attempt:
            chan_attempt_id = self.chan_attempt.id
            self._check_and_update_chan_guess_hints_for_lang(chan_image)
            letters = self.chan_attempt.get_shown_letters(self.lang.alpha2)
            words_lengths = self.chan_attempt.get_words_lengths(self.lang.alpha2)
        else:
            chan_attempt_id = None
            chan_name = self._get_chan_name_by_chan_image(chan_image)
            words_letters_result = self._get_words_letters_result(chan_name)
            letters = words_letters_result.letters
            words_lengths = words_letters_result.words_lengths

        return ChanAttemptResult(
            attempt_id=chan_attempt_id,
            chan_image_url=deep_getattr(chan_image, 'image', 'url'),
            letters=letters,
            words_lengths=words_lengths,
        ) if chan_image else ChanAttemptResult()

    def _get_chan_image(self) -> Optional[ChanImage]:
        """Get chan image from UserChanImageAttempt"""
        result_chan_image = None

        # Get pending chan image
        if pending_chan_attempt := UserChanImageAttempt.objects.filter(
            user=self.user,
            mode=self.mode,
            is_pending=True,
            is_shown=False,
        ).last():
            self.chan_attempt = pending_chan_attempt
            result_chan_image = self.chan_attempt.chan_image

        # Get chan image from previous attempt (with 10% chance)
        if not result_chan_image and self._is_lucky_to_show_previous_attempt():
            yesterday = timezone.localtime(timezone.now()) - timedelta(days=1)
            result_chan_image = self._get_chan_image_from_unsolved(created_lte=yesterday)

        # Create new attempt
        if not result_chan_image:
            showed_chans_ids = UserChanImageAttempt.objects.filter(
                user=self.user,
                mode=self.mode,
            ).values_list('chan_image__chan__id', flat=True)
            new_chan = Chan.objects.filter(
                ~Q(id__in=showed_chans_ids),
            ).order_by('?').first()
            if new_chan:
                result_chan_image = ChanImage.objects.filter(chan=new_chan).order_by('?').first()
                chan_name = self._get_chan_name_by_chan_image(result_chan_image)
                words_letters_result = self._get_words_letters_result(chan_name)
                new_chan_attempt = UserChanImageAttempt.objects.create(
                    user=self.user,
                    mode=self.mode,
                    chan_image=result_chan_image,
                    guess_hints={
                        self.lang.alpha2: {
                            'shown_letters': words_letters_result.letters,
                            'words_lengths': words_letters_result.words_lengths,
                            'correct_answer': chan_name,
                        },
                    },
                )
                self.chan_attempt = new_chan_attempt

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
            chan_image__chan_id__in=Subquery(
                UserChanImageAttempt.objects.filter(
                    user=self.user,
                    mode=self.mode,
                    is_shown=True,
                ).values_list('chan_image__chan_id', flat=True),
            ),
        ).order_by('?').first()

        if unsolved_attempt:
            # Clone previous unsolved attempt to new attempt
            unsolved_attempt.pk = None
            unsolved_attempt.is_pending = True

            # Get one of the suitable chan images if there are several
            chan_image = ChanImage.objects.filter(
                chan=unsolved_attempt.chan_image.chan,
            ).order_by('?').first()

            chan_name = self._get_chan_name_by_chan_image(chan_image)
            words_letters_result = self._get_words_letters_result(chan_name)

            unsolved_attempt.guess_hints = {
                self.lang.alpha2: {
                    'shown_letters': words_letters_result.letters,
                    'words_lengths': words_letters_result.words_lengths,
                    'correct_answer': chan_name,
                },
            }

            unsolved_attempt.given_answer = ''
            unsolved_attempt.chan_image = chan_image
            unsolved_attempt.save()

            self.chan_attempt = unsolved_attempt

            return chan_image

        return None


class ShuffledWordsLettersGenerator:
    """Class for generating letters shuffled with random letters"""

    _LANG_LETTERS = {
        'en': {'vowels': 'AEIOU', 'consonants': 'BCDFGHJKLMNPQRSTVWXYZ'},
        'ru': {'vowels': 'АЕИОУЫЭЮЯ', 'consonants': 'БВГДЖЗЙКЛМНПРСТФХЦЧШЩ'},
        'de': {'vowels': 'AEIOUÄÖÜ', 'consonants': 'BCDFGHJKLMNPQRSTVWXYZß'},
    }

    def __init__(self, lang_alpha2: str):
        self.lang_alpha2 = lang_alpha2 or DEFAULT_LANG

    def get_result_letters(self, source_string: str) -> WordsLettersResult:
        words_lengths = [len(word) for word in source_string.strip().split(' ')]
        result_letters = [ch for ch in list(source_string.upper()) if ch.strip()]
        result_letters = self._add_random_letters_with_same_lang(result_letters)
        random.shuffle(result_letters)
        return WordsLettersResult(
            words_lengths=words_lengths,
            letters=result_letters,
        )

    def _add_random_letters_with_same_lang(self, letters: list[str]) -> list[str]:
        """Method to add random letters with same lang.
        Should add n = len(letters) random letters with n/2 vowels and n/2 consonants"""

        vowels = self._LANG_LETTERS.get(self.lang_alpha2).get('vowels')
        consonants = self._LANG_LETTERS.get(self.lang_alpha2).get('consonants')

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


class UserAttemptLogGenerator:
    _CORRECT = 'Guessed'
    _INCORRECT = 'Incorrect'
    _SHOWN_CORRECT = 'Viewed answer'
    _PENDING = 'Wait for guess'
    _UNKNOWN = 'Unknown'
    _HIDDEN = '-'

    def __init__(self, user: User):
        self.user = user

    @cached_property
    def lang_alpha2(self) -> Lang:
        """Return lang for user or default"""
        return deep_getattr(self.user, 'lang', 'alpha2') or DEFAULT_LANG

    def get_user_attempt_logs(self) -> list[UserAttemptLog]:
        user_attempt_logs = []
        attempts = UserChanImageAttempt.objects.filter(
            user=self.user,
        ).select_related('chan_image').order_by('-id')
        for attempt in attempts:
            user_status = self._calculate_user_status(
                is_pending=attempt.is_pending,
                is_solved=attempt.is_solved,
                is_shown=attempt.is_shown,
            )
            correct = self._HIDDEN
            correct_answer = attempt.get_correct_answer(getattr(attempt.answer_lang, 'alpha2', ''))
            if user_status in [self._SHOWN_CORRECT, self._CORRECT] and correct_answer:
                correct = correct_answer
            user_attempt_logs.append(UserAttemptLog(
                id=attempt.id,
                image_url=attempt.chan_image.image.url,
                status=user_status,
                answer=attempt.given_answer or self._HIDDEN,
                correct=correct,
                date=attempt.created,
            ))
        return user_attempt_logs

    def _calculate_user_status(
        self,
        is_pending: bool,
        is_solved: bool,
        is_shown: bool,
    ) -> str:
        if is_solved:
            return self._CORRECT
        elif is_shown:
            return self._SHOWN_CORRECT
        elif is_pending:
            return self._PENDING
        else:
            return self._INCORRECT
