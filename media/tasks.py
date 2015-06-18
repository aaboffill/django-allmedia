# coding=utf-8
import os
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='media.generate_thumbnails')
def create_thumbnails(image_path, usage):
    from .settings import MEDIA_THUMBNAIL_SIZES
    from .utils import generate_thumbnail
    try:
        for size, method in MEDIA_THUMBNAIL_SIZES[usage]:
            generate_thumbnail(image_path, size, method)
    except KeyError as e:
        logger.exception(e)


@shared_task(name='media.create_thumbnail')
def create_thumbnail(image_path, size, method):
    from .utils import generate_thumbnail
    generate_thumbnail(image_path, size, method)


@shared_task(name='media.clean_temp_files')
def clean_temp_files():
    from .models import AjaxFileUploaded
    from datetime import datetime, timedelta
    try:
        temp_files = AjaxFileUploaded.objects.filter(date__lt=datetime.now()-timedelta(days=1))
        for temp_file in temp_files:
            os.remove(temp_file.file.path)
        temp_files.delete()
    except Exception as e:
        logger.exception(e)


@shared_task(name='media.follow_youtube_video_processing')
def follow_youtube_video_processing(video_id, user_id):
    from .models import YoutubeVideo
    from .storage.youtube import PROCESSING_STATUS
    from django.contrib.auth.models import User

    try:
        user = User.objects.get(pk=user_id)
        video = YoutubeVideo.objects.get(pk=video_id)
        logger.info('Executing follow_youtube_video_processing task for the video %s' % video)

        logger.info('Setting the user %s to the youtube file storage' % user)
        setattr(video.file.storage, 'user', user)
        if video.file.status == PROCESSING_STATUS:
            logger.info('Enqueue follow_youtube_video_processing task for the video %s in 60 seconds' % video)
            follow_youtube_video_processing.delay(video_id, user_id, countdown=60)
        else:
            logger.info('Completed youtube processing for the video %s' % video)

    except Exception as e:
        logger.exception(e)