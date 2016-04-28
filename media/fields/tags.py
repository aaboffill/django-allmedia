# coding=utf-8
from django import forms
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.encoding import force_text
from media.widgets.tags import TagSelectHiddenInput


class ModelMultiTagSelectChoiceField(forms.ModelMultipleChoiceField):
    """A MultipleChoiceField whose choices are a model QuerySet."""
    widget = TagSelectHiddenInput

    def __init__(self, show_as='', register_choice=False, *args, **kwargs):
        super(ModelMultiTagSelectChoiceField, self).__init__(*args, **kwargs)
        self.show_as = show_as
        self.register_choice = register_choice

    def to_python(self, value):
        if value and not isinstance(value, (list, tuple, self)):
            value = value.split(',')
        return super(ModelMultiTagSelectChoiceField, self).to_python(value)

    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')
        elif not self.required and not value:
            return self.queryset.none()
        value = value.split(',')
        key = self.to_field_name or 'pk'
        values_to_update = []
        for pk in value:
            try:
                self.queryset.filter(**{key: pk})
            except ValueError:
                if self.register_choice and not isinstance(pk, int):
                    obj, created = self.queryset.model.objects.get_or_create(name=pk)
                    values_to_update.append((pk, force_text(obj.pk)))
                else:
                    raise ValidationError(
                        self.error_messages['invalid_pk_value'],
                        code='invalid_pk_value',
                        params={'pk': pk},
                    )
        for to_update in values_to_update:
            value.remove(to_update[0])
            value.append(to_update[1])
        qs = self.queryset.filter(**{'%s__in' % key: value})
        pks = set([force_text(getattr(o, key)) for o in qs])
        for val in value:
            if force_text(val) not in pks:
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )
        # Since this overrides the inherited ModelChoiceField.clean
        # we run custom validators here
        self.run_validators(value)
        return qs

    def prepare_value(self, value):
        if (hasattr(value, '__iter__') and
                not isinstance(value, six.text_type) and
                not hasattr(value, '_meta')):
            value = [super(forms.ModelMultipleChoiceField, self).prepare_value(v) for v in value]
        else:
            value = super(forms.ModelMultipleChoiceField, self).prepare_value(value)

        if not value:
            return value
        values = value if isinstance(value, list) else [value]
        key = self.to_field_name or 'pk'
        result = []
        for pk in values:
            try:
                obj = self.queryset.get(**{key: pk})
                show_as = getattr(obj, self.show_as, False)
                text = str(obj) if not show_as else show_as() if callable(show_as) else show_as
                result.append({'id': obj.pk, 'text': text})
            except self.queryset.model.DoesNotExist:
                raise ValidationError(
                    self.error_messages['invalid_pk_value'],
                    code='invalid_pk_value',
                    params={'pk': pk},
                )
        return result
