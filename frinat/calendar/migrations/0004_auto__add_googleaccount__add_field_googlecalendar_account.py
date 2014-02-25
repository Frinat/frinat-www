# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GoogleAccount'
        db.create_table(u'calendar_googleaccount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('credentials', self.gf('oauth2client.django_orm.CredentialsField')(null=True)),
        ))
        db.send_create_signal(u'calendar', ['GoogleAccount'])

        # Adding field 'GoogleCalendar.account'
        db.add_column(u'calendar_googlecalendar', 'account',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['calendar.GoogleAccount']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'GoogleAccount'
        db.delete_table(u'calendar_googleaccount')

        # Deleting field 'GoogleCalendar.account'
        db.delete_column(u'calendar_googlecalendar', 'account_id')


    models = {
        u'calendar.googleaccount': {
            'Meta': {'object_name': 'GoogleAccount'},
            'credentials': ('oauth2client.django_orm.CredentialsField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'calendar.googlecalendar': {
            'Meta': {'object_name': 'GoogleCalendar'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['calendar.GoogleAccount']"}),
            'calendar_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'calendar.googlecalendarplugin': {
            'Meta': {'object_name': 'GoogleCalendarPlugin', 'db_table': "u'cmsplugin_googlecalendarplugin'", '_ormbases': ['cms.CMSPlugin']},
            'calendars_to_display': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['calendar.GoogleCalendar']", 'symmetrical': 'False'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'calendar.monthcalendarplugin': {
            'Meta': {'object_name': 'MonthCalendarPlugin', 'db_table': "u'cmsplugin_monthcalendarplugin'", '_ormbases': ['cms.CMSPlugin']},
            'calendars_to_display': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Calendar']", 'symmetrical': 'False'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'display_details': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'schedule.calendar': {
            'Meta': {'object_name': 'Calendar'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['calendar']