# coding=utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, DeleteView
from media.forms import VideoAjaxUploadForm, YoutubeVideoAjaxUploadForm
from media.models import Video, YoutubeVideo
from .views import (ListMediaItem, CreateMedia, DetailMedia,
                    UpdateMedia, CreateMultipleYoutubeVideos, ShowMultipleYoutubeVideos)
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # ADMIN URLS
    url(r'^admin/', include(admin.site.urls)),

    # media urls
    url(
        r'^media/', include('media.urls')
    ),

    url(
        r'^test/$',
        TemplateView.as_view(template_name='test/test.html'),
        name="test"
    ),

    # list
    url(
        r'^test/video/list/$',
        ListMediaItem.as_view(
            template_name='test/list.html',
            model=Video
        ),
        name="list_video"
    ),
    url(
        r'^test/youtubevideo/list/$',
        ListMediaItem.as_view(
            template_name='test/list.html',
            model=YoutubeVideo
        ),
        name="list_youtubevideo"
    ),

    # create
    url(
        r'^test/video/create/$',
        CreateMedia.as_view(
            template_name='test/create_update.html',
            model=Video,
            form_class=VideoAjaxUploadForm,
            success_url=reverse_lazy('list_video')
        ),
        name="create_video"
    ),
    url(
        r'^test/youtubevideo/create/$',
        CreateMedia.as_view(
            template_name='test/create_update.html',
            model=YoutubeVideo,
            form_class=YoutubeVideoAjaxUploadForm,
            success_url=reverse_lazy('list_youtubevideo')
        ),
        name="create_youtubevideo"
    ),

    # update
    url(
        r'^test/video/update/(?P<pk>\d+)/$',
        UpdateMedia.as_view(
            template_name='test/create_update.html',
            model=Video,
            form_class=VideoAjaxUploadForm,
            success_url=reverse_lazy('list_video')
        ),
        name="update_video"
    ),
    url(
        r'^test/youtubevideo/update/(?P<pk>\d+)/$',
        UpdateMedia.as_view(
            template_name='test/create_update.html',
            model=YoutubeVideo,
            form_class=YoutubeVideoAjaxUploadForm,
            success_url=reverse_lazy('list_youtubevideo')
        ),
        name="update_youtubevideo"
    ),

    # detail
    url(
        r'^test/video/detail/(?P<pk>\d+)/$',
        DetailMedia.as_view(
            model=Video,
            template_name='test/video/detail.html'
        ),
        name="detail_video"
    ),
    url(
        r'^test/youtubevideo/detail/(?P<pk>\d+)/$',
        DetailMedia.as_view(
            model=YoutubeVideo,
            template_name='test/youtube/detail.html'
        ),
        name="detail_youtubevideo"
    ),

    # delete
    url(
        r'^test/video/delete/(?P<pk>\d+)/$',
        DeleteView.as_view(
            model=Video,
            success_url=reverse_lazy('list_video')
        ),
        name="delete_video"
    ),
    url(
        r'^test/youtubevideo/delete/(?P<pk>\d+)/$',
        DeleteView.as_view(
            model=YoutubeVideo,
            success_url=reverse_lazy('list_youtubevideo')
        ),
        name="delete_youtubevideo"
    ),

###########################################################
    url(
        r'^test/youtubevideo/multiple/create/$',
        CreateMultipleYoutubeVideos.as_view(
            template_name='test/multi_videos/create_update.html',
            model=YoutubeVideo,
            form_class=YoutubeVideoAjaxUploadForm,
            success_url=reverse_lazy('list_youtubevideo')
        ),
        name="create_youtubevideo_multi"
    ),
    url(
        r'^test/youtubevideo/multiple/detail/$',
        ShowMultipleYoutubeVideos.as_view(
            template_name='test/multi_videos/detail.html',
        ),
        name="detail_youtubevideo_multi"
    ),
)

# FOR UPLOADED MEDIA
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)