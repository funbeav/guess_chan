from functools import cached_property

from common.utils import deep_getattr
from game.constants import DEFAULT_LANG
from game.generators import ChanAttemptGenerator
from game.models import CharacterImage, UserChanImageAttempt
from game.objects import AttemptAnswerResult, ChanAttemptResult
from project.models import Lang


class GameProcessor:
    """Describes game process for certain user"""

    def __init__(self, user, show_correct_answer: bool = False):
        self.user = user
        self.show_correct_answer = show_correct_answer  # TO DO: user settings to show correct answer by default

    @cached_property
    def lang(self) -> Lang:
        """Return lang for user or default"""
        return getattr(self.user, 'lang', None) or Lang.objects.get(alpha2=DEFAULT_LANG)

    def process_answer(self, answer: str, attempt_id: int) -> AttemptAnswerResult:
        """Get result of answering on chan_image_id and modify last UserChanImageAttempt"""

        answer_result = AttemptAnswerResult(given_answer=answer, attempt_id=attempt_id)
        if not attempt_id:
            raise Exception(f"Attempt ID is not provided")

        last_attempt = UserChanImageAttempt.objects.filter(user=self.user).last()

        if not last_attempt:
            raise Exception(f"No last attempt")

        if last_attempt.id != attempt_id:
            raise Exception(f"Attempt [{attempt_id}] does not fit the last attempt [{last_attempt.id}]")

        correct_answer = last_attempt.get_correct_answer(self.lang.alpha2)

        # If there is pending attempt mark it as not pending, and solved if correct
        if last_attempt.is_pending:
            self.user.change_energy(-1) if self.user else None
            if answer.upper() == correct_answer.upper():
                last_attempt.is_solved = True
                last_attempt.is_shown = True
                answer_result.is_correct = True
            last_attempt.is_pending = False
            last_attempt.given_answer = answer
            last_attempt.answer_lang = self.lang
            last_attempt.save(commit=bool(self.user))
        # If need to show correct answer - mark last attempt as shown (if not shown previously)
        # If anon user - show answer for single pending attempt. TO DO: everyday clear single attempt for anon user
        elif self.show_correct_answer:
            self.show_answer(last_attempt)
        else:
            raise Exception(f"There is no pending Attempt [{attempt_id}]")

        if answer_result.is_correct or self.show_correct_answer:
            answer_result.correct_answer = correct_answer
            answer_result.character_image_url = deep_getattr(
                CharacterImage.objects.filter(character=last_attempt.chan_image.chan.character).first(), 'image', 'url',
            )
        return answer_result

    def show_answer(self, chan_attempt: UserChanImageAttempt):
        if not chan_attempt.is_shown:
            chan_attempt.is_shown = True
            chan_attempt.save(commit=bool(self.user))
        else:
            raise Exception(f"Chan for this Chan Image [{chan_attempt.chan_image.id}] was already shown")

    def get_chan_attempt(self) -> ChanAttemptResult:
        """Get next one chan_image for user if available"""
        if getattr(self.user, 'energy', 1) > 0:
            if chan_image_result := ChanAttemptGenerator(self.user).get_next_chan_attempt():
                return chan_image_result
            else:
                raise Exception(f"Available Chan not found")
        else:
            raise Exception(f"Out of energy")
