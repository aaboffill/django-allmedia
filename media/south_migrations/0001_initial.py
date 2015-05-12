# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MediaTag'
        db.create_table(u'media_mediatag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site'])),
        ))
        db.send_create_signal(u'media', ['MediaTag'])

        # Adding unique constraint on 'MediaTag', fields ['name', 'site']
        db.create_unique(u'media_mediatag', ['name', 'site_id'])

        # Adding model 'Media'
        db.create_table(u'media_media', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content_type_set_for_media', to=orm['contenttypes.ContentType'])),
            ('object_pk', self.gf('django.db.models.fields.TextField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_media', null=True, to=orm['auth.User'])),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='media', null=True, to=orm['media.MediaAlbum'])),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site'])),
        ))
        db.send_create_signal(u'media', ['Media'])

        # Adding M2M table for field tags on 'Media'
        m2m_table_name = db.shorten_name(u'media_media_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('media', models.ForeignKey(orm[u'media.media'], null=False)),
            ('mediatag', models.ForeignKey(orm[u'media.mediatag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['media_id', 'mediatag_id'])

        # Adding model 'Image'
        db.create_table(u'media_image', (
            (u'media_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['media.Media'], unique=True, primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=255)),
        ))
        db.send_create_signal(u'media', ['Image'])

        # Adding model 'Video'
        db.create_table(u'media_video', (
            (u'media_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['media.Media'], unique=True, primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
        ))
        db.send_create_signal(u'media', ['Video'])

        # Adding model 'Attachment'
        db.create_table(u'media_attachment', (
            (u'media_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['media.Media'], unique=True, primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
        ))
        db.send_create_signal(u'media', ['Attachment'])

        # Adding model 'MediaAlbum'
        db.create_table(u'media_mediaalbum', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content_type_set_for_mediaalbum', to=orm['contenttypes.ContentType'])),
            ('object_pk', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cover', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='cover_of', unique=True, null=True, to=orm['media.Media'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site'])),
        ))
        db.send_create_signal(u'media', ['MediaAlbum'])

        # Adding model 'AjaxFileUploaded'
        db.create_table(u'media_ajaxfileuploaded', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'media', ['AjaxFileUploaded'])


    def backwards(self, orm):
        # Removing unique constraint on 'MediaTag', fields ['name', 'site']
        db.delete_unique(u'media_mediatag', ['name', 'site_id'])

        # Deleting model 'MediaTag'
        db.delete_table(u'media_mediatag')

        # Deleting model 'Media'
        db.delete_table(u'media_media')

        # Removing M2M table for field tags on 'Media'
        db.delete_table(db.shorten_name(u'media_media_tags'))

        # Deleting model 'Image'
        db.delete_table(u'media_image')

        # Deleting model 'Video'
        db.delete_table(u'media_video')

        # Deleting model 'Attachment'
        db.delete_table(u'media_attachment')

        # Deleting model 'MediaAlbum'
        db.delete_table(u'media_mediaalbum')

        # Deleting model 'AjaxFileUploaded'
        db.delete_table(u'media_ajaxfileuploaded')


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
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['media']