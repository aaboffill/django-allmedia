# coding=utf-8
import json
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from . import settings
from .fields.tags import ModelMultiTagSelectChoiceField
from .validators import FileFieldValidator
from .decorators import ajax_file_upload
from .models import MediaAlbum, Image, Video, MediaTag, Attachment, AjaxFileUploaded, YoutubeVideo


class MediaAlbumForm(forms.ModelForm):
    """
    Form to add a media album
    """
    class Meta:
        model = MediaAlbum
        fields = ('name', 'location', 'private')


class MediaForm(forms.ModelForm):
    """
    Form to add a media object
    """
    tags = ModelMultiTagSelectChoiceField(
        register_choice=True, queryset=MediaTag.on_site.all(), required=False, help_text=_(u"Enter tag's name.")
    )

    class Meta:
        fields = ('caption', 'private', 'file', 'tags', 'creator')
        widgets = {
            'creator': forms.HiddenInput(),
        }

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None):
        super(MediaForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                        empty_permitted, instance)
        self.fields['file'].widget.template_with_initial = '%(input)s'


class ObjectMediaForm(MediaForm):

    class Meta(MediaForm.Meta):
        fields = ('content_type', 'object_pk', 'caption', 'private', 'file', 'tags', 'creator')


class MediaAdminForm(forms.ModelForm):
    pass


# IMAGE FORMS
class ImageForm(MediaForm):
    """
    Form to add an image
    """
    class Meta(MediaForm.Meta):
        model = Image


@ajax_file_upload(form_file_field_name="file", content_type="image")
class ImageAjaxUploadForm(ImageForm):
    pass


class ObjectImageForm(ObjectMediaForm):

    class Meta(ObjectMediaForm.Meta):
        model = Image


@ajax_file_upload(form_file_field_name="file", content_type="image")
class ObjectImageAjaxUploadForm(ObjectImageForm):
    pass


class ImageAdminForm(MediaAdminForm):

    class Meta:
        model = Image


# VIDEO FORMS
class VideoForm(MediaForm):
    """
    Form to add a video
    """

    class Meta(MediaForm.Meta):
        model = Video


@ajax_file_upload(form_file_field_name="file", content_type="video")
class VideoAjaxUploadForm(VideoForm):
    pass


class ObjectVideoForm(ObjectMediaForm):

    class Meta(ObjectMediaForm.Meta):
        model = Video


@ajax_file_upload(form_file_field_name="file", content_type="video")
class ObjectVideoAjaxUploadForm(ObjectVideoForm):
    pass


class VideoAdminForm(MediaAdminForm):

    class Meta:
        model = Video


# YOUTUBE VIDEO FORMS
class YoutubeVideoForm(MediaForm):
    """
    Form to add a video
    """

    class Meta(MediaForm.Meta):
        model = YoutubeVideo

    def save(self, commit=True):
        self.instance.file.field.tags = [tag.name for tag in self.cleaned_data['tags']]
        return super(YoutubeVideoForm, self).save(commit)


@ajax_file_upload(form_file_field_name="file", content_type="video")
class YoutubeVideoAjaxUploadForm(YoutubeVideoForm):
    pass


class ObjectYoutubeVideoForm(ObjectMediaForm):

    class Meta(ObjectMediaForm.Meta):
        model = YoutubeVideo

    def save(self, commit=True):
        self.instance.file.field.tags = [tag.name for tag in self.cleaned_data['tags']]
        return super(ObjectYoutubeVideoForm, self).save(commit)


@ajax_file_upload(form_file_field_name="file", content_type="video")
class ObjectYoutubeVideoAjaxUploadForm(ObjectYoutubeVideoForm):
    pass


class YoutubeVideoAdminForm(MediaAdminForm):

    class Meta:
        model = YoutubeVideo

    def save(self, commit=True):
        self.instance.file.field.tags = [tag.name for tag in self.cleaned_data['tags']]
        return super(YoutubeVideoAdminForm, self).save(commit)


# ATTACHMENT FORMS
class AttachmentForm(MediaForm):

    class Meta(MediaForm.Meta):
        model = Attachment


@ajax_file_upload(form_file_field_name="file", content_type="all")
class AttachmentAjaxUploadForm(AttachmentForm):
    pass


class ObjectAttachmentForm(ObjectMediaForm):

    class Meta(ObjectMediaForm.Meta):
        model = Attachment


@ajax_file_upload(form_file_field_name="file", content_type="all")
class ObjectAttachmentAjaxUploadForm(ObjectAttachmentForm):
    pass


class AttachmentAdminForm(MediaAdminForm):

    class Meta:
        model = Attachment


class TagForm(forms.ModelForm):
    """
    Form to add a media tag
    """
    class Meta:
        model = MediaTag
        fields = ('name',)


class AjaxFileUploadedForm(forms.ModelForm):

    class Meta:
        model = AjaxFileUploaded
        fields = ('file',)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, content="all"):
        super(AjaxFileUploadedForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                                   empty_permitted, instance)
        # setting file validators
        self.fields['file'].validators.append(FileFieldValidator(
            mime_types=settings.MEDIA_STATICFILES_FORMATS[content]['types'],
            max_size=settings.MEDIA_STATICFILES_FORMATS[content]['size']
        ))