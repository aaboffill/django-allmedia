# coding=utf-8
import json
from django.forms import HiddenInput
from django.forms.util import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html


class TagSelectHiddenInput(HiddenInput):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            final_attrs.update(
                {'data-select2-initial': json.dumps(value)}
            )
            value = [v['id'] for v in value]
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))
        return format_html('<input{0} />', flatatt(final_attrs))