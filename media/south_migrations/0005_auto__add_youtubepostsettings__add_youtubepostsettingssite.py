# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'YoutubePostSettings'
        db.create_table(u'media_youtubepostsettings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post_url', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'media', ['YoutubePostSettings'])

        # Adding M2M table for field post_tags on 'YoutubePostSettings'
        m2m_table_name = db.shorten_name(u'media_youtubepostsettings_post_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('youtubepostsettings', models.ForeignKey(orm[u'media.youtubepostsettings'], null=False)),
            ('mediatag', models.ForeignKey(orm[u'media.mediatag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['youtubepostsettings_id', 'mediatag_id'])

        # Adding model 'YoutubePostSettingsSite'
        db.create_table(u'media_youtubepostsettingssite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('youtube_post_settings', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['media.YoutubePostSettings'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'], unique=True)),
        ))
        db.send_create_signal(u'media', ['YoutubePostSettingsSite'])


    def backwards(self, orm):
        # Deleting model 'YoutubePostSettings'
        db.delete_table(u'media_youtubepostsettings')

        # Removing M2M table for field post_tags on 'YoutubePostSettings'
        db.delete_table(db.shorten_name(u'media_youtubepostsettings_post_tags'))

        # Deleting model 'YoutubePostSettingsSite'
        db.delete_table(u'media_youtubepostsettingssite')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'media.ajaxfileuploaded': {
            'Meta': {'object_name': 'AjaxFileUploaded'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'media.attachment': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Attachment', '_ormbases': [u'media.Media']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            u'media_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['media.Media']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'media.image': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Image', '_ormbases': [u'media.Media']},
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '255'}),
            u'media_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['media.Media']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'media.media': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Media'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'media'", 'null': 'True', 'to': u"orm['media.MediaAlbum']"}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_media'", 'to': u"orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_media'", 'null': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'media'", 'blank': 'True', 'to': u"orm['media.MediaTag']"})
        },
        u'media.mediaalbum': {
            'Meta': {'ordering': "['caption']", 'object_name': 'MediaAlbum'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_mediaalbum'", 'to': u"orm['contenttypes.ContentType']"}),
            'cover': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'cover_of'", 'unique': 'True', 'null': 'True', 'to': u"orm['media.Media']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"})
        },
        u'media.mediatag': {
            'Meta': {'unique_together': "(('name', 'site'),)", 'object_name': 'MediaTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"})
        },
        u'media.video': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Video', '_ormbases': [u'media.Media']},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            u'media_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['media.Media']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'media.youtubepostsettings': {
            'Meta': {'object_name': 'YoutubePostSettings'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'youtube_post_settings'", 'blank': 'True', 'to': u"orm['media.MediaTag']"}),
            'post_url': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'youtube_post_settings'", 'symmetrical': 'False', 'through': u"orm['media.YoutubePostSettingsSite']", 'to': u"orm['sites.Site']"})
        },
        u'media.youtubepostsettingssite': {
            'Meta': {'object_name': 'YoutubePostSettingsSite'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']", 'unique': 'True'}),
            'youtube_post_settings': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['media.YoutubePostSettings']"})
        },
        u'media.youtubeuploadprogress': {
            'Meta': {'object_name': 'YoutubeUploadProgress'},
            'progress_data': ('media.fields.files.JSONField', [], {'max_length': '250'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        },
        u'media.youtubevideo': {
            'Meta': {'ordering': "['-created']", 'object_name': 'YoutubeVideo', '_ormbases': [u'media.Media']},
            'file': ('media.fields.files.YoutubeFileField', [], {'max_length': '255'}),
            u'media_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['media.Media']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['media']