import random

from datetime import timedelta
from typing import Optional

from django.db.models import Subquery, Q
from django.utils import timezone

from game.constants import NORMAL_MODE
from game.models import Chan, ChanImage, UserChanImageAttempt


class ChanImageGenerator:
    """Generates Chan Batches for current user"""

    def __init__(self, user, mode=NORMAL_MODE):
        self.user = user
        self.mode = mode

    def get_next_chan_image(self) -> Optional[ChanImage]:
        return self._get_chan_image()

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