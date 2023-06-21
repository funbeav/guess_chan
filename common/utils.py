import functools
import os
import uuid


def generate_filename(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join(f'images/{instance.image_folder}', f'{uuid.uuid4()}.{ext}')


def deep_getattr(obj, *attrs, default=None):
    """Getattr in cycle."""
    result = obj
    for attr in attrs:
        result = getattr(result, attr, default)
    return result
