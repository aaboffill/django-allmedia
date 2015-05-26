# coding=utf-8
import os
from django.core.exceptions import ImproperlyConfigured
from django.forms import ValidationError
from django.db.models.signals import pre_save, post_delete
from .fields.files import YoutubeFileField
from . import remove_old_files, remove_files
from .models import AjaxFileUploaded
from .signals import pre_ajax_file_save


def ajax_file_upload(form_file_field_name="file", model_file_field_name=None, content_type="all"):

    def decorator(cls):
        from django import forms
        if not issubclass(cls, forms.ModelForm):
            raise ImproperlyConfigured("ajax_file_upload decorator is only suitable for ModelForm descendants.")

        setattr(cls, 'file_field_required', cls.base_fields.get(form_file_field_name).required)

        class Meta:
            proxy = True

        def model_save(self, force_insert=False, force_update=False, using=None, update_fields=None):
            # finds if self has a temp_file attribute
            if getattr(self, "temp_file", None):
                temp_file = getattr(self, "temp_file")
                # connect with pre_ajax_file_save signal
                pre_ajax_file_save.send(self.__class__, instance=self)
                # create the new field field instance
                getattr(self, model_file_field_name if model_file_field_name else form_file_field_name).save(
                    os.path.basename(temp_file.file.path),
                    temp_file.file.file,
                    False
                )

            super(ProxyModel, self).save(force_insert, force_update, using, update_fields)

        ProxyModel = type(
            "%sAjaxProxy" % cls.Meta.model.__name__,
            (cls.Meta.model,),
            {
                '__module__': cls.Meta.model.__module__,
                'Meta': Meta,
                'save': model_save
            }
        )

        pre_save.connect(remove_old_files, sender=ProxyModel)
        post_delete.connect(remove_files, sender=ProxyModel)

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


def ajax_file_formset_upload(func):
    if not callable(func):
        raise ImproperlyConfigured("ajax_file_formset_upload decorator is only suitable for callable objects.")

    from django import forms

    def new_func(model, form=forms.ModelForm, *args, **kwargs):
        if not issubclass(form.Meta.model, model):
            raise ImproperlyConfigured("Incompatible model and form class.")

        model = form.Meta.model
        return func(model, form, *args, **kwargs)

    return new_func


def show_youtube_upload_process(fields=None, model=None, save_method=None):
    if not fields:
        fields = []

    def decorator(cls):
        from django.views.generic import CreateView, UpdateView
        from django.db.models import Model
        if (not model or not save_method) and not issubclass(cls, (CreateView, UpdateView)):
            raise ImproperlyConfigured("If the model or save_method args are not specified, "
                                       "then show_youtube_upload_process decorator is only suitable "
                                       "for CreateView or UpdateView descendants.")

        if model and not issubclass(model, Model):
            raise ImproperlyConfigured("model arg must be a Model descendants.")

        # Save method
        normal_save_method = getattr(cls, save_method or 'form_valid')

        def method(self, *args, **kwargs):
            current_model = model or getattr(self, 'model')
            all_youtube_fields = len(fields) == 0
            # finding youtube fields
            for field in current_model._meta.fields:
                if not isinstance(field, YoutubeFileField):
                    continue

                if all_youtube_fields or field.name in fields:
                    setattr(field.storage, 'request', getattr(self, 'request', None))

            return normal_save_method(self, *args, **kwargs)

        setattr(cls, save_method or 'form_valid', method)

        return cls

    return decorator