# coding=utf-8
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from .fields.files import YoutubeFileField, JSONField
from .storage.youtube import PROCESSING_STATUS
from .settings import MEDIA_LOCATIONS
from .signals import pre_ajax_file_save


class MediaTag(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    site = models.ForeignKey(Site, default=settings.SITE_ID, verbose_name=_('site'))

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        unique_together = ('name', 'site')

    def __unicode__(self):
        return u"%s" % self.name


class MediaManagerMixin(object):

    def for_object(self, obj):
        return self.filter(content_type__pk=ContentType.objects.get_for_model(obj).pk, object_pk=obj.pk)


class MediaManager(MediaManagerMixin, models.Manager):
    pass


class CurrentSiteMediaManager(MediaManagerMixin, CurrentSiteManager):
    pass


class Media(models.Model):
    media_type = 'all'

    # Content-object field
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    creator = models.ForeignKey(User, related_name="created_media", verbose_name=_('creator'), null=True, blank=True)
    caption = models.CharField(max_length=200, verbose_name=_('caption'), null=True, blank=True)
    album = models.ForeignKey('MediaAlbum', verbose_name=_('album'), related_name='media', null=True,
                              blank=True)
    private = models.BooleanField(_('private'), default=False)

    tags = models.ManyToManyField(MediaTag, verbose_name=_('tags'), related_name="media", blank=True)

    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    site = models.ForeignKey(Site, default=settings.SITE_ID, verbose_name=_('site'))

    objects = MediaManager()
    on_site = CurrentSiteMediaManager()

    class Meta:
        ordering = ['-created', ]

    def __unicode__(self):
        return u"%s" % self.caption or self.created

    def tag_list(self, sep=","):
        return sep.join([tag.name for tag in self.tags.all()])

    def description(self):
        return self.caption

    def is_private(self):
        return self.private

    def location_template(self, file_type):
        model = '%s.%s' % (self.content_object._meta.app_label, self.content_object._meta.object_name.lower())
        templates = MEDIA_LOCATIONS.setdefault(file_type, {})
        return templates.get(model, templates.get('default'))

    def upload_to(self, filename):
        from .utils import process_filename
        return self.location_template(self.media_type) % {
            "site": settings.SITE_ID,
            "model": '%s_%s' % (self.content_object._meta.app_label, self.content_object._meta.object_name.lower()),
            "pk": self.content_object.pk,
            "filename": process_filename(filename)
        }

    @property
    def filename(self):
        return os.path.split(self.file.name)[1]


class ImageManagerMixin(object):

    def for_object(self, obj):
        return self.filter(content_type__pk=ContentType.objects.get_for_model(obj).pk, object_pk=obj.pk)


class ImageManager(ImageManagerMixin, models.Manager):
    pass


class CurrentSiteImageManager(ImageManagerMixin, CurrentSiteManager):
    pass


class Image(Media):
    """
    Represents an image.
    """
    media_type = 'image'
    file = models.ImageField(_('file'), upload_to=Media.upload_to, max_length=255)

    objects = ImageManager()
    on_site = CurrentSiteImageManager()


class VideoManagerMixin(object):

    def for_object(self, obj):
        return self.filter(content_type__pk=ContentType.objects.get_for_model(obj).pk, object_pk=obj.pk)


class VideoManager(VideoManagerMixin, models.Manager):
    pass


class CurrentSiteVideoManager(VideoManagerMixin, CurrentSiteManager):
    pass


class Video(Media):
    """
    Represents a video.
    """
    media_type = 'video'
    file = models.FileField(_('file'), upload_to=Media.upload_to, max_length=255)

    objects = VideoManager()
    on_site = CurrentSiteVideoManager()


class YoutubeVideoManagerMixin(object):

    def for_object(self, obj):
        return self.filter(content_type__pk=ContentType.objects.get_for_model(obj).pk, object_pk=obj.pk)


class YoutubeVideoManager(YoutubeVideoManagerMixin, models.Manager):
    pass


class CurrentSiteYoutubeVideoManager(YoutubeVideoManagerMixin, CurrentSiteManager):
    pass


class YoutubeVideo(Media):

    media_type = 'youtube'
    file = YoutubeFileField(
        _('youtube file'),
        upload_to=Media.upload_to,
        max_length=255,
        privacy=Media.is_private,
        comment=Media.description,
        tags=Media.tag_list
    )

    objects = YoutubeVideoManager()
    on_site = CurrentSiteYoutubeVideoManager()

    @property
    def is_processed(self):
        return self.file.status != PROCESSING_STATUS


class AttachmentManagerMixin(object):

    def for_object(self, obj):
        return self.filter(content_type__pk=ContentType.objects.get_for_model(obj).pk, object_pk=obj.pk)


class AttachmentManager(AttachmentManagerMixin, models.Manager):
    pass


class CurrentSiteAttachmentManager(AttachmentManagerMixin, CurrentSiteManager):
    pass


class Attachment(Media):
    """
    Represents a general attachment.
    """
    file = models.FileField(_('file'), upload_to=Media.upload_to, max_length=255)

    objects = AttachmentManager()
    on_site = CurrentSiteAttachmentManager()


class MediaAlbum(models.Model):
    # Content-object field
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    name = models.CharField(_('name'), max_length=100, blank=False, null=False)
    caption = models.CharField(_('caption'), max_length=200, null=True, blank=True)
    location = models.CharField(_('location'), max_length=200, null=True, blank=True)
    owner = models.ForeignKey(User, verbose_name=_('owner'), null=True, blank=True)
    private = models.BooleanField(_('private'), default=False)
    cover = models.OneToOneField(Media, related_name='cover_of', verbose_name=_('cover'), null=True, blank=True)

    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    site = models.ForeignKey(Site, default=settings.SITE_ID, verbose_name=_('site'))

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        ordering = ['caption', ]

    def __unicode__(self):
        return u"%s" % self.name


# Set Media's content object after corresponding MediaAlbum's content object
def set_content_after_album_content(instance, **kwargs):
    if (instance.content_type_id is None) and (instance.object_pk == u''):
        album = MediaAlbum.on_site.get(pk=instance.album_id)
        instance.content_type_id = album.content_type_id
        instance.object_pk = album.object_pk

# Connecting to Image, Video and Attachment pre_save signal
pre_save.connect(set_content_after_album_content, sender=Image, dispatch_uid='set_image_content_after_album_content')
pre_save.connect(set_content_after_album_content, sender=Video, dispatch_uid='set_video_content_after_album_content')
pre_save.connect(set_content_after_album_content, sender=Attachment, dispatch_uid='set_attachment_content_after_album_content')
# Connecting to Image, Video and Attachment pre_ajax_file_save signal
pre_ajax_file_save.connect(set_content_after_album_content, sender=Image, dispatch_uid='set_ajax_image_content_after_album_content')
pre_ajax_file_save.connect(set_content_after_album_content, sender=Video, dispatch_uid='set_ajax_video_content_after_album_content')
pre_ajax_file_save.connect(set_content_after_album_content, sender=Attachment, dispatch_uid='set_ajax_attachment_content_after_album_content')


class AjaxFileUploaded(models.Model):

    def upload_to(self, filename):
        from .utils import process_filename
        return 'site-%s/temp/ajax_files/%s/%s' % (
            settings.SITE_ID,
            '%s_%s' % (self._meta.app_label, self._meta.object_name.lower()),
            process_filename(filename)
        )

    file = models.FileField(verbose_name=_('ajax file'), max_length=255, upload_to=upload_to)
    date = models.DateTimeField(auto_now=True, verbose_name=_('date'))


class YoutubeUploadProgress(models.Model):
    session_key = models.CharField(_('session key'), max_length=40, primary_key=True)
    progress_data = JSONField(_('progress data'), max_length=250)


class YoutubePostSettings(models.Model):
    post_url = models.BooleanField(_("post site url"), default=False)
    post_tags = models.ManyToManyField(MediaTag, verbose_name=_('tags'), related_name="youtube_post_settings", blank=True)

    sites = models.ManyToManyField(Site, verbose_name=_("sites"), related_name="youtube_post_settings", through="YoutubePostSettingsSite")

    class Meta:
        verbose_name_plural = "youtube post settings"

    def __unicode__(self):
        return ", ".join([site.name for site in self.sites.all()])


class YoutubePostSettingsSite(models.Model):
    youtube_post_settings = models.ForeignKey(YoutubePostSettings, verbose_name="youtube post settings")
    site = models.ForeignKey(Site, unique=True)