from functools import cached_property
from typing import Optional

from common.utils import deep_getattr
from game.constants import DEFAULT_LANG
from game.generators import ChanAttemptGenerator
from game.models import CharacterImage, UserChanImageAttempt
from game.objects import AttemptAnswerResult, ChanAttemptResult
from project.models import Lang


class GameProcessor:
    """Describes game process for certain user"""

    def __init__(self, user, need_to_show_correct: bool = False):
        self.user = user
        self.need_to_show_correct = need_to_show_correct  # TO DO: user settings to show correct answer by default

    @cached_property
    def lang(self) -> Lang:
        """Return lang for user or default"""
        return getattr(self.user, 'lang', None) or Lang.objects.get(alpha2=DEFAULT_LANG)

    def process_answer(self, answer: str, attempt_id: int) -> AttemptAnswerResult:
        """Get result of answering on chan_image_id and modify last UserChanImageAttempt"""

        answer_result = AttemptAnswerResult(given_answer=answer, attempt_id=attempt_id)
        if not attempt_id:
            raise Exception(f"Attempt ID is not provided")

        chan_attempt = UserChanImageAttempt.objects.filter(id=attempt_id).first()

        if not chan_attempt:
            raise Exception(f"Chan attempt [{attempt_id}] not found")

        correct_answer = chan_attempt.get_correct_answer(self.lang.alpha2)

        # If there is pending attempt mark it as not pending, and solved if correct
        if chan_attempt.is_pending:
            self.user.change_energy(-1) if self.user else None
            if answer.upper() == correct_answer.upper():
                chan_attempt.is_solved = True
                chan_attempt.is_shown = True
                answer_result.is_correct = True
            chan_attempt.is_pending = False
            chan_attempt.given_answer = answer
            chan_attempt.answer_lang = self.lang
            chan_attempt.save(commit=bool(self.user))
        else:
            raise Exception(f"Chan attempt [{attempt_id}] is not pending")

        shown_result = self.show_answer(attempt_id) if (
            not chan_attempt.is_shown and self.need_to_show_correct
        ) else AttemptAnswerResult()

        if answer_result.is_correct or self.need_to_show_correct:
            answer_result.correct_answer = correct_answer
            answer_result.character_image_url = shown_result.character_image_url or deep_getattr(
                CharacterImage.objects.filter(character=chan_attempt.chan_image.chan.character).first(), 'image', 'url',
            )
        return answer_result

    def show_answer(self, attempt_id: int) -> AttemptAnswerResult:
        """
        If need to show correct answer - mark attempt as shown (if not shown previously)
        If anon user - show answer for single pending attempt. TO DO: everyday clear single attempt for anon user
        """

        chan_attempt = UserChanImageAttempt.objects.filter(id=attempt_id).first()
        if not chan_attempt:
            raise Exception(f"Chan attempt [{attempt_id}] not found")

        if not chan_attempt.is_shown:
            chan_attempt.is_shown = True
            chan_attempt.is_pending = False
            chan_attempt.save(commit=bool(self.user))
        else:
            raise Exception(f"Chan for this Chan Image [{chan_attempt.chan_image.id}] already shown")

        return AttemptAnswerResult(
            attempt_id=attempt_id,
            correct_answer=chan_attempt.get_correct_answer(chan_attempt.answer_lang.alpha2),
            character_image_url=deep_getattr(
                CharacterImage.objects.filter(character=chan_attempt.chan_image.chan.character).first(), 'image', 'url',
            ),
        )

    def get_attempt(self) -> ChanAttemptResult:
        """Get next one chan_image for user if available"""
        if getattr(self.user, 'energy', 1) > 0:
            if chan_image_result := ChanAttemptGenerator(self.user).get_next_chan_attempt():
                return chan_image_result
            else:
                raise Exception(f"Available Chan not found")
        else:
            raise Exception(f"Out of energy")
