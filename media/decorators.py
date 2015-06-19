# coding=utf-8
import os
from django.core.exceptions import ImproperlyConfigured
from django.forms import ValidationError
from functools import wraps
from django.utils.decorators import available_attrs
from .models import AjaxFileUploaded
from .signals import pre_ajax_file_save


def ajax_file_upload(form_file_field_name="file", model_file_field_name=None, content_type="all"):

    def decorator(cls):
        from django import forms
        if not issubclass(cls, forms.ModelForm):
            raise ImproperlyConfigured("ajax_file_upload decorator is only suitable for ModelForm descendants.")

        setattr(cls, 'file_field_required', cls.base_fields.get(form_file_field_name).required)

        original_model = cls.Meta.model

        class Meta:
            proxy = True

        def model_save(self, force_insert=False, force_update=False, using=None, update_fields=None):
            # finds if self has a temp_file attribute
            if getattr(self, "temp_file", None):
                temp_file = getattr(self, "temp_file")
                # connect with pre_ajax_file_save signal
                pre_ajax_file_save.send(original_model, instance=self)
                # create the new field field instance
                getattr(self, model_file_field_name if model_file_field_name else form_file_field_name).save(
                    os.path.basename(temp_file.file.path),
                    temp_file.file.file,
                    False
                )

            self.__class__ = original_model
            original_model.save(self, force_insert, force_update, using, update_fields)

        def model_delete(self, using=None):
            self.__class__ = original_model
            original_model.delete(self, using)

        ProxyModel = type(
            "%sAjaxProxy" % original_model.__name__,
            (original_model,),
            {
                '__module__': original_model.__module__,
                'Meta': Meta,
                'save': model_save,
                'delete': model_delete
            }
        )

        # Init method
        normal_init_method = getattr(cls, '__init__')

        def __init__(self, *args, **kwargs):
            normal_init_method(self, *args, **kwargs)

            if not self.instance.pk is None:
                self.instance = ProxyModel.objects.get(pk=self.instance.pk)

            # create a temporal field to save the ajax file uploaded id
            self.fields['temp_file_id'] = forms.IntegerField(
                required=False,
                widget=forms.HiddenInput(attrs={"class": "temp_file_id"})
            )
             # set target field as non required
            self.fields[form_file_field_name].required = False
            # to render an attribute with the content type
            self.fields[form_file_field_name].widget.attrs.update({"data-contentvalidation": content_type})

        setattr(cls, '__init__', __init__)

        if cls.file_field_required:
            # clean method
            normal_clean_method = getattr(cls, 'clean')

            def clean(self):
                cleaned_data = normal_clean_method(self)
                if not cleaned_data.get('temp_file_id', None) and not cleaned_data.get(form_file_field_name, None):
                    raise ValidationError(message="No file provided", code="no_file")
                return cleaned_data

            setattr(cls, 'clean', clean)

        # model
        setattr(cls.Meta, 'model', ProxyModel)
        setattr(cls._meta, 'model', ProxyModel)

        # save method
        normal_save_method = getattr(cls, 'save')

        def save(self, commit=True, **kwargs):
            # gets the temp_file_id
            temp_file_id = self.cleaned_data.get('temp_file_id', False)
            if temp_file_id:
                try:
                    temp_file = AjaxFileUploaded.objects.get(pk=temp_file_id)
                    instance = normal_save_method(self, commit=False, **kwargs)
                    # set a new attribute temp_file to the form instance
                    setattr(instance, "temp_file", temp_file)

                    if commit:
                        instance.save()
                        self.save_m2m()

                    return instance
                except AjaxFileUploaded.DoesNotExist:
                    return normal_save_method(self, commit, **kwargs)
                except Exception as e:
                    raise e
            else:
                return normal_save_method(self, commit, **kwargs)

        setattr(cls, 'save', save)

        return cls

    return decorator


def ajax_file_generic_inlineformset_upload(func):
    if not callable(func):
        raise ImproperlyConfigured("ajax_file_generic_inlineformset_upload decorator is only suitable for callable objects.")

    from django import forms

    def new_func(model, form=forms.ModelForm, *args, **kwargs):
        if not issubclass(form.Meta.model, model):
            raise ImproperlyConfigured("Incompatible model and form class.")

        model = form.Meta.model
        return func(model, form, *args, **kwargs)

    return new_func


def ajax_file_inlineformset_upload(func):
    if not callable(func):
        raise ImproperlyConfigured("ajax_file_inlineformset_upload decorator is only suitable for callable objects.")

    from django import forms

    def new_func(parent_model, model, form=forms.ModelForm, *args, **kwargs):
        if not issubclass(form.Meta.model, model):
            raise ImproperlyConfigured("Incompatible model and form class.")

        model = form.Meta.model
        return func(parent_model, model, form, *args, **kwargs)

    return new_func


def use_youtube_api(model_attributes):

    def decorator(func):
        if not callable(func):
            raise ImproperlyConfigured("use_youtube_api decorator is only suitable for callable objects.")

        @wraps(func, assigned=available_attrs(func))
        def new_func(self, *args, **kwargs):
            from django.views.generic import View
            from django.db.models import Model
            from .fields.files import YoutubeFileField

            if not isinstance(self, View):
                raise ImproperlyConfigured("use_youtube_api decorator is only suitable for django View descendants.")

            if model_attributes and isinstance(model_attributes, (list, set, tuple)):
                for attr_name in model_attributes:
                    attr_split = attr_name.split('.')
                    attr_split_length = len(attr_split)
                    if attr_split_length > 1:
                        for i in xrange(attr_split_length):
                            if i == 0:
                                model = getattr(self, attr_split[i])
                            else:
                                model = getattr(model, attr_split[i])
                    else:
                        model = getattr(self, attr_name)
                    if not model or not issubclass(model, Model):
                        continue

                    # finding youtube fields
                    for field in model._meta.fields:
                        if not isinstance(field, YoutubeFileField):
                            continue

                        setattr(field.storage, 'request', getattr(self, 'request', None))

            return func(self, *args, **kwargs)
        return new_func

    return decorator