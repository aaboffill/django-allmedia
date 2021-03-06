# coding=utf-8
from django.contrib import admin
from .models import YoutubePostSettings, YoutubePostSettingsSite, MediaTag


class YoutubePostSettingsSiteInline(admin.StackedInline):
    model = YoutubePostSettingsSite


class YoutubePostSettingsAdmin(admin.ModelAdmin):
    inlines = (YoutubePostSettingsSiteInline,)
    filter_horizontal = ('post_tags',)


admin.site.register(YoutubePostSettings, YoutubePostSettingsAdmin)
admin.site.register(MediaTag)