import random

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from game.models import ChanImage, UserChanImageAttempt, Chan
from guess_chan.settings import NORMAL_MODE, EASY_MODE, HARD_MODE


class ChanImageGenerator:
    """Generates Chan Batches for current user"""

    BATCH_LENGTH = {
        EASY_MODE: 2,
        NORMAL_MODE: 4,
        HARD_MODE: 6,
    }

    def __init__(self, user, mode=NORMAL_MODE):
        self.user = user
        self.mode = mode

    def get_next_chan_image(self):
        return self._get_chan_image()

    def _get_chan_image(self):
        """Get chan image from UserChanImageAttempt"""
        # TO DO: cache already gotten self.chan_images
        result_chan_image = None

        # Get pending chan image
        if pending_chan_attempt := UserChanImageAttempt.objects.filter(
            user=self.user,
            mode=self.mode,
            is_pending=True,
        ).first():
            result_chan_image = pending_chan_attempt.chan_image

        # Get chan image from previous attempt (with 10% chance)
        if not result_chan_image and self._is_show_previous_attempt():
            yesterday = timezone.localtime(timezone.now()) - timedelta(days=1)
            result_chan_image = self._get_unsolved_chan_image(created_lte=yesterday)

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
            result_chan_image = self._get_unsolved_chan_image(
                created_lte=timezone.localtime(timezone.now()),
            )

        return result_chan_image

    @staticmethod
    def _is_show_previous_attempt():
        return random.randint(1, 10) == 1   # 10% chance

    def _get_unsolved_chan_image(self, created_lte):
        """Get unsolved chans from the past (<= created_lte)"""
        unsolved_attempt = UserChanImageAttempt.objects.filter(
            user=self.user,
            mode=self.mode,
            is_solved=False,
            created__lte=created_lte,
        ).order_by('?').first()
        if unsolved_attempt:
            unsolved_attempt.is_pending = True
            unsolved_attempt.save()
            return ChanImage.objects.filter(
                chan=unsolved_attempt.chan,
            ).order_by('?').first() if unsolved_attempt else None
        return None
