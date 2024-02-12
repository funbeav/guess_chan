import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from game.services import ChanService
from django.conf import settings


class Command(BaseCommand):
    help = "Initialize start chans from .init_chans folder."
    _init_chans_folder = Path(__file__).absolute().parent.parent.parent.parent / settings.INIT_CHANS_FOLDER
    _sample_chan_folder_name = "Sample"

    def handle(self, *args, **options):
        self.stdout.write('Loading init chans...')
        for chan_folder_name in os.listdir(self._init_chans_folder):
            chan_folder_path = os.path.join(self._init_chans_folder, chan_folder_name)
            if os.path.isdir(chan_folder_path) and chan_folder_name != self._sample_chan_folder_name:
                self._process_chan_folder(chan_folder_path)
                self.stdout.write()
        self.stdout.write('Finish.')

    def _process_chan_folder(self, chan_folder_path):
        # Get folder name
        folder_name = os.path.basename(chan_folder_path)
        self.stdout.write("Folder name: " + folder_name)

        # Get full paths to chan images
        chan_images_path = os.path.join(chan_folder_path, "chan")
        chan_image_paths = list(self._get_full_paths(chan_images_path))
        self.stdout.write("Full paths to chan images:")
        for path in chan_image_paths:
            self.stdout.write(path)

        # Get full paths to character images
        character_images_path = os.path.join(chan_folder_path, "character")
        character_image_paths = list(self._get_full_paths(character_images_path))
        self.stdout.write("Full paths to character images:")
        for path in character_image_paths:
            self.stdout.write(path)

        # Get dict with langs and their values from names.json
        names_json_path = os.path.join(chan_folder_path, "names.json")
        with open(names_json_path, "r", encoding='utf-8-sig') as names_file:
            names_data = json.load(names_file)
        self.stdout.write("Dict with langs and their values:")
        self.stdout.write(str(names_data))

        ChanService().create_chan(
            character_name=folder_name,
            chan_image_paths=chan_image_paths,
            character_image_paths=character_image_paths,
            langs=names_data,
        )

    @staticmethod
    def _get_full_paths(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                yield os.path.join(root, file)
