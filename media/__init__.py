# coding=utf-8
from . import settings
from django.db.models.signals import pre_save, post_delete
from .fields.files import YoutubeFileField
from .models import Media


def find_models_with_file_field():
    from django.db import models
    result = []
    for model in models.get_models():
        for field in model._meta.fields:
            if isinstance(field, models.FileField):
                result.append(model)
                break
    return result


def remove_old_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
    except instance.DoesNotExist:
        return

    from django.db import models
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        old_file = getattr(old_instance, field.name)
        new_file = getattr(instance, field.name)
        if old_file != new_file:
            old_file.delete(save=False)
        elif isinstance(field, YoutubeFileField):
            # youtube title
            old_title = old_file.field.title if not callable(old_file.field.title) else old_file.field.title(old_instance)
            new_title = new_file.field.title if not callable(new_file.field.title) else new_file.field.title(instance)
            title = new_title if old_title != new_title else None
            # youtube privacy
            old_privacy = old_file.field.privacy if not callable(old_file.field.privacy) else old_file.field.privacy(old_instance)
            new_privacy = new_file.field.privacy if not callable(new_file.field.privacy) else new_file.field.privacy(instance)
            privacy = new_privacy if old_privacy != new_privacy else None
            # youtube comment
            old_comment = old_file.field.comment if not callable(old_file.field.comment) else old_file.field.comment(old_instance)
            new_comment = new_file.field.comment if not callable(new_file.field.comment) else new_file.field.comment(instance)
            comment = new_comment if old_comment != new_comment else None
            # youtube tags
            if isinstance(instance, Media):
                old_tags = old_instance.tag_list()
                new_tags = new_file.field.tags if not callable(new_file.field.tags) else new_file.field.tags(instance)
                if isinstance(new_tags, list):
                    new_tags = ','.join(new_tags)
            else:
                old_tags = old_file.field.tags if not callable(old_file.field.tags) else old_file.field.tags(old_instance)
                new_tags = new_file.field.tags if not callable(new_file.field.tags) else new_file.field.tags(instance)
            tags = new_tags if old_tags != new_tags else None

            if title or privacy or comment or tags:
                old_file.update(title, privacy, comment, tags if not tags or isinstance(tags, list) else tags.split(','))


def remove_files(sender, instance, **kwargs):
    from django.db import models
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        getattr(instance, field.name).delete(save=False)


def connect_signals():
    for model in find_models_with_file_field():
        pre_save.connect(remove_old_files, sender=model)
        post_delete.connect(remove_files, sender=model)