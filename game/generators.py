import random

from datetime import datetime, timedelta, time

from game.models import ChanImage, UserChanBatch
from guess_chan.settings import NORMAL_MODE, EASY_MODE, HARD_MODE


class BatchGenerator:
    """Generates Chan Batches for current user"""

    BATCH_LENGTH = {
        EASY_MODE: 2,
        NORMAL_MODE: 4,
        HARD_MODE: 6,
    }

    def __init__(self, user, mode=NORMAL_MODE):
        self.user = user
        self.mode = mode
        self.chan_images = self._get_chan_images()

    def get_next_chan_image(self):
        return self.chan_images[0]

    def _get_chan_images(self):
        """Get or create batch with Chans (maybe better ChanImages?) for User. (!TO DO!) No Chan repeat in each batch"""
        # TO DO: cache already gotten self.chan_images
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        batch_query = UserChanBatch.objects.filter(
            user=self.user,
            mode=self.mode,
            time__gte=datetime.combine(today, time()),
            time__lte=datetime.combine(tomorrow, time()),
        )
        if not batch_query.exists():
            # TO DO: exclude passed long ago chan_images (ChanImageLog?)
            result_chan_images = ChanImage.objects.order_by('?')[:self.BATCH_LENGTH[self.mode]]
            UserChanBatch.objects.bulk_create([
                UserChanBatch(user=self.user, mode=self.mode, chan=chan_image.chan)
                for chan_image in result_chan_images
            ])
        else:
            unsolved_chans_ids = batch_query.filter(is_solved=False).values_list('chan', flat=True).order_by('?')
            # TO DO: exclude passed chan_images (ChanImageLog)
            result_chan_images = ChanImage.objects.filter(chan_id__in=unsolved_chans_ids).order_by('?')
        return result_chan_images
