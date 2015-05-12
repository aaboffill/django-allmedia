# coding=utf-8
import os
import re
import unicodedata

from django.utils import six

from .settings import (MEDIA_IMAGE_EXTENSION, MEDIA_IMAGE_FORMAT, MEDIA_IMAGE_QUALITY,
                       MEDIA_NORMALIZE_FILENAME, MEDIA_CONVERT_FILENAME)


def thumbnail_path(path, size, method):
    """
    Returns the path for the resized image.
    """

    directory, name = os.path.split(path)
    image_name, ext = name.rsplit('.', 1)
    return os.path.join(directory, '%s_%s_%s.%s' % (image_name, method, size, MEDIA_IMAGE_EXTENSION))


def generate_thumbnail(path, size, method):
    try:
        import Image
    except ImportError:
        try:
            from PIL import Image
        except ImportError:
            raise ImportError('Cannot import the Python Image Library.')

    image = Image.open(path)

    # normalize image mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # parse size string 'WIDTHxHEIGHT'
    width, height = [int(i) for i in size.split('x')]

    # use PIL methods to edit images
    if method == 'scale':
        image.thumbnail((width, height), Image.ANTIALIAS)
        image.save(thumbnail_path(path, size, method), MEDIA_IMAGE_FORMAT, quality=MEDIA_IMAGE_QUALITY)

    elif method == 'crop':
        try:
            import ImageOps
        except ImportError:
            from PIL import ImageOps

        ImageOps.fit(
            image, (width, height), Image.ANTIALIAS
        ).save(thumbnail_path(path, size, method), MEDIA_IMAGE_FORMAT, quality=MEDIA_IMAGE_QUALITY)


def convert_filename(value):
    """
    Convert Filename. # from django-filebrowser
    """
    if MEDIA_NORMALIZE_FILENAME:
        chunks = value.split(os.extsep)
        normalized = []
        for v in chunks:
            v = unicodedata.normalize('NFKD', six.text_type(v)).encode('ascii', 'ignore').decode('ascii')
            v = re.sub(r'[^\w\s-]', '', v).strip()
            normalized.append(v)

        if len(normalized) > 1:
            value = '.'.join(normalized)
        else:
            value = normalized[0]

    if MEDIA_CONVERT_FILENAME:
        value = value.replace(" ", "_").lower()

    return value