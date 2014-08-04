from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from . import models


class GoogleAccountAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'authorized',
        'show_auth_link',
    ]

admin.site.register(models.GoogleAccount, GoogleAccountAdmin)


class CategoryAdmin(MPTTModelAdmin):
    list_display = [
        'name',
        'path',
    ]

admin.site.register(models.Category, CategoryAdmin)


class GoogleCalendarAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category_path',
        'account',
    ]

    def category_path(self, obj):
        return obj.category.path()
    category_path.short_description = 'Category'

admin.site.register(models.GoogleCalendar, GoogleCalendarAdmin)
