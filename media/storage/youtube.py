# coding=utf-8
from django.contrib.sites.models import Site
from django.core.files.storage import Storage as DjangoStorage
from django.core.files import File
from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile
from django.core.cache import cache
from django.conf import settings
from allauth.socialaccount.models import SocialToken
from ..models import YoutubePostSettings

import httplib
import httplib2
import os
import random
import time
import logging
import json

from apiclient import discovery, errors, http
from oauth2client.client import GoogleCredentials
from oauth2client import GOOGLE_TOKEN_URI
import sys

logger = logging.getLogger(__name__)


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error, IOError, httplib.NotConnected,
    httplib.IncompleteRead, httplib.ImproperConnectionState,
    httplib.CannotSendRequest, httplib.CannotSendHeader,
    httplib.ResponseNotReady, httplib.BadStatusLine
)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# This OAuth 2.0 access scope allows an application to upload files and for full
# read/write access to the authenticated user's YouTube channel.
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
privacy_status = getattr(settings, 'YOUTUBE_DEFAULT_PRIVACY_STATUS', 0)
try:
    DEFAULT_PRIVACY_STATUS = VALID_PRIVACY_STATUSES[privacy_status]
except IndexError:
    DEFAULT_PRIVACY_STATUS = VALID_PRIVACY_STATUSES[0]
except TypeError:
    try:
        VALID_PRIVACY_STATUSES.index(privacy_status)
        DEFAULT_PRIVACY_STATUS = privacy_status
    except ValueError:
        DEFAULT_PRIVACY_STATUS = VALID_PRIVACY_STATUSES[1]

DEFAULT_CATEGORY = getattr(settings, 'YOUTUBE_DEFAULT_CATEGORY', 22)

BASE_URL = getattr(settings, 'YOUTUBE_BASE_URL', 'http://www.youtube.com/embed/%s')
# string to be added in the video ID while is processing
PROCESSING_STATUS = 'processing'
PROCESSED_STATUS = 'processed'
SUCCEEDED_STATUS = 'succeeded'
REJECTED_STATUS = 'rejected'

UPLOAD_CHUNK_SIZE = getattr(settings, 'YOUTUBE_UPLOAD_CHUNK_SIZE', -1)
if UPLOAD_CHUNK_SIZE != 1 and UPLOAD_CHUNK_SIZE % 256 != 0:
    raise "The chunk size value must be divisible by 256"


# This method implements an exponential backoff strategy to resume a failed upload.
def resumable_upload(title, insert_request, size, request=None):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logger.info("Uploading file - %s" % title)
            status, response = insert_request.next_chunk()
            if response and 'id' in response:
                logger.info("Video id '%s' was successfully uploaded." % response['id'])
                if request:
                    if cache:
                        delete_progress_from_cache(request.session.session_key)
                    else:
                        delete_progress_from_db(request.session.session_key)
            elif not response and status:
                if UPLOAD_CHUNK_SIZE != -1 and request:
                    youtube_progress = {
                        'title': title,
                        'resumable_progress': status.resumable_progress,
                        'resumable_progress_MB': '%.2f' % (status.resumable_progress / 1048576.00),
                        'total_size': status.total_size,
                        'total_size_MB': '%.2f' % (status.total_size / 1048576.00),
                    }

                    if cache:
                        save_progress_in_cache(request.session.session_key, youtube_progress)
                    else:
                        save_progress_in_db(request.session.session_key, youtube_progress)
            else:
                logger.error("The upload failed with an unexpected response: %s" % response)
        except errors.HttpError, e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
                logger.error(error)
            else:
                raise
        except RETRIABLE_EXCEPTIONS, e:
            error = "A retriable error occurred: %s" % e
            logger.error(error)

    if error is not None:
        print error
        retry += 1
        if retry > MAX_RETRIES:
            logger.error("No longer attempting to retry.")

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        logger.info("Sleeping %f seconds and then retrying..." % sleep_seconds)
        time.sleep(sleep_seconds)

    return json.dumps({'id': response['id'], 'status': PROCESSING_STATUS, 'size': size})


def save_progress_in_db(key, youtube_progress):
    from media.models import YoutubeUploadProgress

    youtube_upload_progress = YoutubeUploadProgress(
        session_key=key,
        progress_data=youtube_progress
    )
    youtube_upload_progress.save()


def delete_progress_from_db(key):
    from media.models import YoutubeUploadProgress

    YoutubeUploadProgress.objects.filter(session_key=key).delete()


def save_progress_in_cache(key, youtube_progress):
    cache.set(key, youtube_progress)


def delete_progress_from_cache(key):
    cache.delete(key)


class FileYoutubeStorage(DjangoStorage):
    """
    File youtube storage
    """

    def _get_authenticated_service(self):
        try:
            if not getattr(self, 'request', getattr(self, 'user', False)):
                error_msg = 'The FileYoutubeStorage class must be a (request or user) attribute specified, you should need to use the use_youtube_api decorator.'
                logger.error(error_msg)
                raise error_msg

            user = getattr(self, 'request').user if getattr(self, 'request', False) else getattr(self, 'user')
            token = SocialToken.objects.get(
                app__provider='google',
                app__sites=Site.objects.get_current() if getattr(self, 'request', False) else Site.objects.get(pk=getattr(self, 'site')),
                account__provider='google',
                account__user=user
            )

            credentials = GoogleCredentials(
                access_token=token.token,
                client_id=token.app.client_id,
                client_secret=token.app.secret,
                refresh_token=token.token_secret,
                token_expiry=token.expires_at,
                token_uri=GOOGLE_TOKEN_URI,
                user_agent=None
            )
            return discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)
        except SocialToken.DoesNotExist:
            error_msg = 'Does not exist a google social token for the user: %s' % user
            logger.error(error_msg)
            raise error_msg
        except Exception as e:
            logger.error(e)
            raise e

    def _open(self, name, mode='rb'):
        pass

    def get_available_name(self, name):
        return os.path.splitext(os.path.basename(name))[0]

    def save(self, name, content, title='', privacy=None, comment='', tags=''):
        """
        Saves new content to the file specified by name. The content should be
        a proper File object or any python file-like object, ready to be read
        from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content)

        name = self.get_available_name(name)
        return self._save(name, content, title, privacy, comment, tags)

    def _save(self, name, content, title='', privacy=None, comment='', tags=''):
        youtube = self._get_authenticated_service()
        site = Site.objects.get_current()
        post_settings = YoutubePostSettings.objects.get(sites=site)
        # predefined youtube site tags
        post_tags = ", ".join([tag.name for tag in post_settings.post_tags.all()])
        tags = "%s, %s" % (post_tags, tags) if tags else post_tags
        # post site url
        if post_settings.post_url:
            comment = "%s (http://%s)" % (comment, site.domain)

        if not isinstance(privacy, bool):
            privacy = DEFAULT_PRIVACY_STATUS
        elif privacy:
            # as private
            privacy = VALID_PRIVACY_STATUSES[1]
        else:
            # as public
            privacy = VALID_PRIVACY_STATUSES[0]

        body = dict(
            snippet=dict(
                title=title or name,
                description=comment,
                tags=tags,
                categoryId=DEFAULT_CATEGORY
            ),
            status=dict(
                privacyStatus=privacy
            )
        )

        if isinstance(content.file, TemporaryUploadedFile):
            media = http.MediaFileUpload(
                content.file.file.name,
                mimetype=content.file.content_type,
                chunksize=UPLOAD_CHUNK_SIZE,
                resumable=True
            )
        elif isinstance(content.file, InMemoryUploadedFile):
            media = http.MediaIoBaseUpload(
                content.file.file,
                mimetype=content.file.content_type,
                chunksize=UPLOAD_CHUNK_SIZE,
                resumable=True
            )
        elif isinstance(content, File):
            media = http.MediaFileUpload(
                content.file.name,
                chunksize=UPLOAD_CHUNK_SIZE,
                resumable=True
            )

        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            # fields='items(id,snippet,status,fileDetails(fileSize))',
            body=body,
            media_body=media
        )

        return resumable_upload(title or name, insert_request, content.size, getattr(self, 'request', None))

    def delete(self, name):
        name = json.loads(name)
        youtube_id = name['id']
        youtube = self._get_authenticated_service()

        try:
            youtube.videos().delete(
                id=youtube_id,
            ).execute()
        except errors.HttpError, e:
            if e.resp.status == 404:
                pass
            else:
                raise

    def update(self, name, title, privacy, comment, tags):
        name = json.loads(name)
        youtube_id = name['id']
        youtube = self._get_authenticated_service()

        video_response = youtube.videos().list(
            id=youtube_id,
            part='snippet,status'
        ).execute()

        if not (video_response['items'] and len(video_response['items']) > 0):
            logger.error("Video '%s' was not found in youtube." % youtube_id)
            sys.exit(1)

        video_snippet = video_response["items"][0]["snippet"]
        video_status = video_response["items"][0]["status"]

        site = post_settings = None

        if title:
            video_snippet["title"] = title
        if comment:
            site = Site.objects.get_current()
            post_settings = YoutubePostSettings.objects.get(sites=site)
            # post site url
            if post_settings.post_url:
                comment = "%s (http://%s)" % (comment, site.domain)

            video_snippet["description"] = comment
        if tags:
            site = Site.objects.get_current() if not site else site
            post_settings = YoutubePostSettings.objects.get(sites=site) if not post_settings else post_settings
            # predefined youtube site tags
            post_tags = ", ".join([tag.name for tag in post_settings.post_tags.all()])
            tags = "%s, %s" % (post_tags, tags)

            video_snippet["tags"] = tags

        if not privacy is None:
            if not isinstance(privacy, bool):
                privacy = DEFAULT_PRIVACY_STATUS
            elif privacy:
                # as private
                privacy = VALID_PRIVACY_STATUSES[1]
            else:
                # as public
                privacy = VALID_PRIVACY_STATUSES[0]
            video_status["privacyStatus"] = privacy

        youtube.videos().update(
            part='snippet,status',
            body=dict(
                snippet=video_snippet,
                status=video_status,
                id=youtube_id
            )
        ).execute()

    def exists(self, name):
        name = json.loads(name)
        youtube_id = name['id']
        youtube = self._get_authenticated_service()

        video_response = youtube.videos().list(
            id=youtube_id,
            part='status',
            fields='items(id,status(uploadStatus))'
        ).execute()

        return True if video_response['items'] and len(video_response['items']) > 0 else False

    def path(self, name):
        return self.url(name)

    def size(self, name):
        name = json.loads(name)
        return name['size']

    def url(self, name):
        return BASE_URL % json.loads(name)['id']

    def status(self, name):
        name = json.loads(name)
        if name['status'] == PROCESSING_STATUS:
            youtube_id = name['id']
            try:
                youtube = self._get_authenticated_service()
            except:
                return name['status'], name['status']

            video_response = youtube.videos().list(
                id=youtube_id,
                part='processingDetails,status',
                fields='items(id,processingDetails(processingStatus),status(uploadStatus,rejectionReason))'
            ).execute()

            if video_response['items'][0]['processingDetails']['processingStatus'] == SUCCEEDED_STATUS:
                youtube_status = video_response['items'][0]['status']
                if youtube_status['uploadStatus'] == REJECTED_STATUS:
                    return youtube_status['rejectionReason'], name['status']
                return youtube_status['uploadStatus'], name['status']
            return PROCESSING_STATUS, name['status']

        return name['status'], name['status']