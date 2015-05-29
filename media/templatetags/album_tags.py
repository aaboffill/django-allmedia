# coding=utf-8
from django import template
from ..models import MediaAlbum, Image, Video, YoutubeVideo, Attachment

register = template.Library()


@register.filter
def images(album):
    return get_media_list(album, Image)


@register.filter
def videos(album):
    return get_media_list(album, Video)


@register.filter
def youtube_videos(album):
    return get_media_list(album, YoutubeVideo)


@register.filter
def attachments(album):
    return get_media_list(album, Attachment)


def get_media_list(album, media):
    if not album:
        return []
    if not isinstance(album, MediaAlbum):
        raise Exception('MediaAlbum instance expected')
    return media.objects.filter(pk__in=album.media.values_list('pk', flat=True))