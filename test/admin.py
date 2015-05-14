# coding=utf-8
from django.contrib import admin
from media.forms import YoutubeVideoAdminForm
from media.models import Video, YoutubeVideo, MediaTag


class YoutubeVideoAdmin(admin.ModelAdmin):
    model = YoutubeVideo
    form = YoutubeVideoAdminForm


admin.site.register(MediaTag)
admin.site.register(Video)
admin.site.register(YoutubeVideo, YoutubeVideoAdmin)