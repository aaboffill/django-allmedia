# coding=utf-8
from django.db.models.fields.files import FieldFile, FileField
from django.utils.translation import ugettext
from ..storage.youtube import PROCESSING_STATUS, FileYoutubeStorage

import json

try:
    from django.utils.encoding import smart_unicode as smart_text
except ImportError:
    from django.utils.encoding import smart_text


class YoutubeFieldFile(FieldFile):

    def __eq__(self, other):
        # Older code may be expecting FileField values to be simple strings.
        # By overriding the == operator, it can remain backwards compatibility.
        try:
            decoded_name = json.loads(self.name)
            if hasattr(other, 'name'):
                return decoded_name['id'] == json.loads(other.name)['id']
            return decoded_name['id'] == other
        except Exception as e:
            return False

    def _get_status(self):
        self._require_file()
        status, old_status = self.storage.status(self.name)
        if status != old_status:
            model = self.field.model.objects.get(**{self.field.name: self.name})
            setattr(model, self.field.name, getattr(model, self.field.name).name.replace(old_status, status))
            model.save()
        return status
    status = property(_get_status)

    def _get_processing_progress(self):
        completed_progress = {
            'time_left_ms': "0 %s" % ugettext(u"Seconds"),
            'parts_processed': 1000,
            'parts_total': 1000,
            'percent': 100
        }

        if self._get_status() != PROCESSING_STATUS:
            return completed_progress
        return self.storage.processing_progress(self.name) or completed_progress
    processing_progress = property(_get_processing_progress)

    def save(self, name, content, save=True):
        name = self.field.generate_filename(self.instance, name)
        self.name = self.storage.save(
            name=name,
            content=content,
            title=self.field.title if not callable(self.field.title) else self.field.title(self.instance),
            privacy=self.field.privacy if not callable(self.field.privacy) else self.field.privacy(self.instance),
            comment=self.field.comment if not callable(self.field.comment) else self.field.comment(self.instance),
            tags=self.field.tags if not callable(self.field.tags) else self.field.tags(self.instance),
        )
        setattr(self.instance, self.field.name, self.name)

        # Update the filesize cache
        self._size = content.size
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()

    def update(self, title, privacy, comment, tags):
        self.storage.update(self.name, title, privacy, comment, tags)


class YoutubeFileField(FileField):
    attr_class = YoutubeFieldFile

    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None,
                 title='', privacy=None, comment='', tags='', **kwargs):
        super(YoutubeFileField, self).__init__(verbose_name, name, upload_to, storage or FileYoutubeStorage(), **kwargs)
        self.title = title
        self.privacy = privacy
        self.comment = comment
        self.tags = tags


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^media.fields\.files\.YoutubeFileField"])
except:
    pass