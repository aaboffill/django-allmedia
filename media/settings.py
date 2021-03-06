# coding=utf-8
import os
from django.conf import settings

MEDIA_LOCATIONS = getattr(settings, 'MEDIA_LOCATIONS', {
    "image": {
        "default": "%(site)s/%(app_label)s/%(model)s/%(unicode)s/images/%(filename)s"
    },
    "video": {
        "default": "%(site)s/%(app_label)s/%(model)s/%(unicode)s/videos/%(filename)s"
    },
    "youtube": {
        "default": "%(site)s/%(app_label)s/%(model)s/%(unicode)s/youtube/%(filename)s"
    },
    "all": {
        "default": "%(site)s/%(app_label)s/%(model)s/%(unicode)s/attachments/%(filename)s"
    }
})

# to remove non ascii characters set MEDIA_NORMALIZE_FILENAME = True
MEDIA_NORMALIZE_FILENAME = getattr(settings, 'MEDIA_NORMALIZE_FILENAME', False)
# to transform white spaces to underscores set MEDIA_CONVERT_FILENAME = True
MEDIA_CONVERT_FILENAME = getattr(settings, 'MEDIA_CONVERT_FILENAME', False)

MEDIA_IMAGE_FORMAT = getattr(settings, 'MEDIA_IMAGE_FORMAT', 'JPEG')
MEDIA_IMAGE_EXTENSION = getattr(settings, 'MEDIA_IMAGE_FORMAT', 'jpg')
MEDIA_IMAGE_QUALITY = getattr(settings, 'MEDIA_IMAGE_FORMAT', 75)

MEDIA_THUMBNAIL_SIZES = getattr(settings, 'MEDIA_THUMBNAIL_SIZES', {})

MEDIA_STATICFILES_FORMATS = getattr(settings, 'MEDIA_STATICFILES_FORMATS', {
    "image": {
        "types": ('image/jpeg', 'image/jpg', 'image/png', 'image/gif'),
        "size": 0
    },
    "video": {
        "types": ('video/mp4',),
        "size": 0
    },
    "docs": {
        "types": (),
        "size": 0
    }
})

all_types = ()
all_size = 0
for key, value in MEDIA_STATICFILES_FORMATS.iteritems():
    all_types += value['types']
    if all_size < value['size']:
        all_size = value['size']

MEDIA_STATICFILES_FORMATS.update({'all': {
    "types": all_types,
    "size": all_size
}})
