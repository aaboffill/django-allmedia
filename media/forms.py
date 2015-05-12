# coding=utf-8
import json
from django import forms
from django.forms.util import ErrorList
from django.utils.datastructures import MultiValueDictKeyError
from . import settings
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
    default_tags = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        fields = ('caption', 'private', 'file', 'tags', 'creator')
        widgets = {
            'tags': forms.TextInput(),
            'creator': forms.HiddenInput(),
        }

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None):
        super(MediaForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                        empty_permitted, instance)
        if instance is not None:
            self.fields['default_tags'].initial = json.dumps([{'id': obj['id'], 'text': obj['name']}
                                                              for obj in instance.tags.values('id', 'name')])
        self.fields['file'].widget.template_with_initial = '%(input)s'

    def full_clean(self):
        """
        For bound forms, convert tags data to list (if not list yet)
        """
        if self.is_bound:
            field_name = self.add_prefix('tags')
            try:
                data = self.data[field_name]
                if not isinstance(data, list) and data:
                    data = data.split(',')
                    self.data[field_name] = [self._get_or_create_tag(tag) for tag in data]
            except MultiValueDictKeyError:
                pass
        return super(MediaForm, self).full_clean()

    def _get_or_create_tag(self, tag):
        """
        Returns id of an existent or new-created tag
        """
        try:
            return int(tag)
        except ValueError as e:
            return MediaTag.on_site.get_or_create(name=tag)[0].pk


class ImageForm(MediaForm):
    """
    Form to add an image
    """
    class Meta(MediaForm.Meta):
        model = Image


@ajax_file_upload(form_file_field_name="file", content_type="image")
class ImageAjaxUploadForm(ImageForm):
    pass


class VideoForm(MediaForm):
    """
    Form to add a video
    """

    class Meta(MediaForm.Meta):
        model = Video


@ajax_file_upload(form_file_field_name="file", content_type="video")
class VideoAjaxUploadForm(VideoForm):
    pass


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


class AttachmentForm(MediaForm):

    class Meta(MediaForm.Meta):
        model = Attachment


@ajax_file_upload(form_file_field_name="file", content_type="all")
class AttachmentAjaxUploadForm(AttachmentForm):
    pass


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