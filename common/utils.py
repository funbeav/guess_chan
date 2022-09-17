import os
import uuid


def generate_filename(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join(f'images/{instance.image_folder}', f'{uuid.uuid4()}.{ext}')
