import os
import imagehash

from io import BytesIO
from django.core.files import File

from PIL import Image

from game.models import Character, Chan, CharacterImage, ChanImage, CharacterName
from project.models import Lang


class ChanService:
    """Service to work with Chans"""

    def create_chan(
        self,
        character_name: str,
        chan_image_paths: list,
        character_image_paths: list,
        langs: dict,
    ):
        character, _ = Character.objects.get_or_create(name=character_name)
        for character_image_path in character_image_paths:
            pil_image = Image.open(character_image_path)
            temp_image = BytesIO()
            file_extension = os.path.splitext(character_image_path)[1].lower()
            save_format = 'JPEG' if file_extension == '.jpg' else file_extension[1:]
            pil_image.save(temp_image, format=save_format)

            if not CharacterImage.objects.filter(
                character=character,
                hash=str(imagehash.average_hash(pil_image)),
            ).exists():
                character_image = CharacterImage(character=character)
                character_image.image.save(os.path.basename(character_image_path), File(temp_image))
                character_image.save()

        chan, _ = Chan.objects.get_or_create(character=character)
        for chan_image_path in chan_image_paths:
            pil_image = Image.open(chan_image_path)
            temp_image = BytesIO()
            file_extension = os.path.splitext(chan_image_path)[1].lower()
            save_format = 'JPEG' if file_extension == '.jpg' else file_extension[1:]
            pil_image.save(temp_image, format=save_format)

            if not ChanImage.objects.filter(
                chan=chan,
                hash=str(imagehash.average_hash(pil_image)),
            ).exists():
                chan_image = ChanImage(chan=chan)
                chan_image.image.save(os.path.basename(chan_image_path), File(temp_image))
                chan_image.save()

        for alpha2, value in langs.items():
            lang = Lang.objects.get(alpha2=alpha2)
            if not CharacterName.objects.filter(
                character=character,
                lang=lang,
                name=value,
            ).exists():
                character_name = CharacterName(character=character, lang=lang, name=value)
                character_name.save()
