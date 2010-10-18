# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing M2M table for field sponsors_to_display on 'SpecificSponsorsPlugin'
        db.delete_table('sponsors_specificsponsorsplugin_sponsors_to_display')

        # Adding M2M table for field sponsors on 'SpecificSponsorsPlugin'
        db.create_table('sponsors_specificsponsorsplugin_sponsors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('specificsponsorsplugin', models.ForeignKey(orm['sponsors.specificsponsorsplugin'], null=False)),
            ('sponsor', models.ForeignKey(orm['sponsors.sponsor'], null=False))
        ))
        db.create_unique('sponsors_specificsponsorsplugin_sponsors', ['specificsponsorsplugin_id', 'sponsor_id'])


    def backwards(self, orm):
        
        # Adding M2M table for field sponsors_to_display on 'SpecificSponsorsPlugin'
        db.create_table('cmsplugin_specificsponsorsplugin_sponsors_to_display', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('specificsponsorsplugin', models.ForeignKey(orm['sponsors.specificsponsorsplugin'], null=False)),
            ('sponsor', models.ForeignKey(orm['sponsors.sponsor'], null=False))
        ))
        db.create_unique('cmsplugin_specificsponsorsplugin_sponsors_to_display', ['specificsponsorsplugin_id', 'sponsor_id'])

        # Removing M2M table for field sponsors on 'SpecificSponsorsPlugin'
        db.delete_table('sponsors_specificsponsorsplugin_sponsors')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'publisher_is_draft': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'publisher_public': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'publisher_draft'", 'unique': 'True', 'null': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'publisher_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'sponsors.specificsponsorsplugin': {
            'Meta': {'object_name': 'SpecificSponsorsPlugin', 'db_table': "'cmsplugin_specificsponsorsplugin'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'sponsors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sponsors.Sponsor']", 'symmetrical': 'False'})
        },
        'sponsors.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['sponsors']
