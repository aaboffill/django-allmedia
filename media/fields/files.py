# coding=utf-8
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.files import FieldFile, FileField
from django.utils.translation import ugettext
from django.utils import six
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
        self._update_status(old_status, status)
        return status
    status = property(_get_status)

    def _update_status(self, old_status, new_status):
        if new_status != old_status:
            model = self.field.model.objects.get(**{self.field.name: self.name})
            setattr(model, self.field.name, getattr(model, self.field.name).name.replace(old_status, new_status))
            model.save()

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


class JSONField(six.with_metaclass(models.SubfieldBase,
                                   models.TextField)):
    """Simple JSON field that stores python structures as JSON strings
    on database.
    """

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return None
        if isinstance(value, six.string_types):
            try:
                return json.loads(value)
            except Exception as e:
                raise ValidationError(str(e))
        else:
            return value

    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        if isinstance(value, six.string_types):
            super(JSONField, self).validate(value, model_instance)
            try:
                json.loads(value)
            except Exception as e:
                raise ValidationError(str(e))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return json.dumps(value)
        except Exception as e:
            raise ValidationError(str(e))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return smart_text(self.get_prep_value(self._get_val_from_obj(obj)))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        return self.get_prep_value(self._get_val_from_obj(obj))


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^media.fields\.files\.YoutubeFileField"])
    add_introspection_rules([], ["^media.fields\.files\.JSONField"])
except:
    pass

