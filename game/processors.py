from django.db.models import Subquery

from common.utils import deep_getattr
from game.generators import ChanImageGenerator, ShuffledWordsLettersGenerator
from game.models import ChanImage, CharacterImage, CharacterName, UserChanImageAttempt
from game.objects import AnswerResult, ChanImageResult


class GameProcessor:
    """Describes game process for certain user"""

    def __init__(self, user, show_correct_answer: bool = False):
        self.user = user
        self.show_correct_answer = show_correct_answer  # TO DO: user settings to show correct answer by default

    def process_answer(self, answer: str, chan_image_id: int) -> AnswerResult:
        """Get result of answering on chan_image_id and modify last UserChanImageAttempt"""

        answer_result = AnswerResult(given_answer=answer, chan_image_id=chan_image_id)
        if not chan_image_id:
            raise Exception(f"Chan Image ID is not provided")

        answered = CharacterName.objects.filter(name__iexact=answer).first()
        correct_chan_image = ChanImage.objects.filter(id=chan_image_id).first()
        if not correct_chan_image:
            raise Exception(f"Chan Image [{chan_image_id}] not found")

        chan_image_attempts = UserChanImageAttempt.objects.filter(user=self.user, chan_image_id=chan_image_id)

        # If there is pending attempt mark it as not pending, and solved if correct
        if chan_image_last_pending_attempt := chan_image_attempts.filter(is_pending=True).last():
            self.user.change_energy(-1) if self.user else None
            if answered and correct_chan_image and answered.character == correct_chan_image.chan.character:
                chan_image_last_pending_attempt.is_solved = True
                chan_image_last_pending_attempt.is_shown = True
                answer_result.is_correct = True
            chan_image_last_pending_attempt.is_pending = False
            chan_image_last_pending_attempt.given_answer = answer
            chan_image_last_pending_attempt.save(commit=bool(self.user))

        if not chan_image_last_pending_attempt and not self.show_correct_answer:
            raise Exception(f"There is no pending Chan Image [{chan_image_id}]")

        # If need to show correct answer - mark last not pending attempt as shown (if not shown previously)
        # If anonymous user - show answer for single pending attempt. TO DO: everyday clear single attempt for anon user
        if self.show_correct_answer:
            is_pending_to_show_correct_answer = False if self.user else True
            if chan_image_last_not_shown_attempt := chan_image_attempts.filter(
                is_pending=is_pending_to_show_correct_answer,
                is_shown=False,
            ).exclude(
                chan_id__in=Subquery(
                    UserChanImageAttempt.objects.filter(
                        user=self.user,
                        is_shown=True,
                        chan=correct_chan_image.chan,
                    ).values_list('chan_id', flat=True),
                )
            ).last():
                chan_image_last_not_shown_attempt.is_shown = True
                chan_image_last_not_shown_attempt.save(commit=bool(self.user))
            else:
                raise Exception(f"Chan for this Chan Image [{correct_chan_image.id}] was already shown")

        if answer_result.is_correct or self.show_correct_answer:
            answer_result.correct_answer = CharacterName.objects.filter(
                character=correct_chan_image.chan.character,
                lang__alpha2='en',
            ).first().name
            answer_result.character_image_url = deep_getattr(
                CharacterImage.objects.filter(character=correct_chan_image.chan.character).first(), 'image', 'url',
            )

        return answer_result

    def get_chan_image_result(self) -> ChanImageResult:
        """Get next one chan_image for user if available"""

        if getattr(self.user, 'energy', 1) > 0:
            chan_image_generator = ChanImageGenerator(self.user)
            if chan_image_result := chan_image_generator.get_next_chan_image_result():
                return chan_image_result
            else:
                raise Exception(f"Available Chan not found")
        else:
            raise Exception(f"Out of energy")
