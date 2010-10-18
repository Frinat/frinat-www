"""CategoryAdmin for Zinnia"""
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

from frinat.people import models


class GroupAdmin(admin.ModelAdmin):
    fields = ('title', 'parent', 'slug')
    list_display = ('title', 'slug', 'tree_path')
    prepopulated_fields = {'slug': ('title', )}
    list_filter = ('parent',)

admin.site.register(models.Group, GroupAdmin)


class PersonAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Person, PersonAdmin)