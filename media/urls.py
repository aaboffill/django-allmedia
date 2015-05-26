# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import HandleAjaxFileUploadedView, HandleYoutubeProcessingView, YoutubeUploadProcessView

urlpatterns = patterns('',
    # BASICS

    url(
        r'^upload/file/$',
        login_required(HandleAjaxFileUploadedView.as_view()),
        name="ajax_upload_file"
    ),

    url(
        r'^youtube/processing/(?P<video_id>\d+)/$',
        HandleYoutubeProcessingView.as_view(),
        name="youtube_processing"
    ),

    url(
        r'^youtube/upload/process/$',
        YoutubeUploadProcessView.as_view(template_name='media/youtube/upload_process.html'),
        name="youtube_upload_process"
    ),

)
