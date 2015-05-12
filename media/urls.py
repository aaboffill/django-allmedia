# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import HandleAjaxFileUploadedView, HandleYoutubeProcessing, YoutubeUploadProcess

urlpatterns = patterns('',
    # BASICS

    url(
        r'^upload/file/$',
        login_required(HandleAjaxFileUploadedView.as_view()),
        name="ajax_upload_file"
    ),

    url(
        r'^youtube/processing/(?P<video_id>\d+)/$',
        HandleYoutubeProcessing.as_view(),
        name="youtube_processing"
    ),

    url(
        r'^youtube/upload/process/$',
        YoutubeUploadProcess.as_view(template_name='media/youtube/upload_process.html'),
        name="youtube_upload_process"
    ),

)
