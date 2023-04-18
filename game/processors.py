from common.utils import deep_getattr
from game.generators import ChanImageGenerator
from game.models import ChanImage, CharacterImage, CharacterName, UserChanImageAttempt
from game.objects import AnswerResult, CorrectAnswer


class GameProcessor:
    """Describes game process for certain user"""

    def __init__(self, user, show_correct_answer: bool = False):
        self.user = user
        self.show_correct_answer = show_correct_answer  # TO DO: user settings to show correct answer by default

    def process_answer(self, answer: str, chan_image_id: int) -> AnswerResult:
        """Get result of answering on chan_image_id and modify last UserChanImageAttempt"""

        is_correct_answer = False
        answered = CharacterName.objects.filter(name__iexact=answer).first()
        correct = ChanImage.objects.filter(id=chan_image_id).first()

        chan_image_attempts = UserChanImageAttempt.objects.filter(user=self.user, chan_image_id=chan_image_id)

        # If there is pending attempt mark it as not pending, and solved if correct
        if chan_image_last_pending_attempt := chan_image_attempts.filter(is_pending=True).last():
            self.user.change_energy(-1)
            if answered and correct and answered.character == correct.chan.character:
                chan_image_last_pending_attempt.is_solved = True
                chan_image_last_pending_attempt.is_shown = True
                is_correct_answer = True
            chan_image_last_pending_attempt.is_pending = False
            chan_image_last_pending_attempt.save()

        # If need to show correct answer - mark last not pending attempt as shown
        if self.show_correct_answer:
            if chan_image_last_not_shown_attempt := chan_image_attempts.filter(
                is_pending=False,
                is_shown=False,
            ).last():
                chan_image_last_not_shown_attempt.is_shown = True
                chan_image_last_not_shown_attempt.save()

        correct_answer = CorrectAnswer(
            text=CharacterName.objects.filter(
                character=correct.chan.character,
                lang__alpha='en',
            ).first().name,
            image_url=deep_getattr(
                CharacterImage.objects.filter(character=correct.chan.character).first(), 'image', 'url'
            ),
        ) if is_correct_answer or self.show_correct_answer else None

        return AnswerResult(
            is_correct=is_correct_answer,
            given_answer=answer,
            correct_answer=correct_answer,
        )

    def get_next_chan_image(self):
        """Get next one chan_image for user if available"""

        message = ''
        chan_image = None
        if getattr(self.user, 'energy', 1) > 0:
            chan_image = ChanImageGenerator(self.user).get_next_chan_image()
            if not chan_image:
                message = 'Chan not found'
        else:
            message = 'Out of energy'

        return chan_image, message
