from django.contrib import admin

from . import models


class GoogleAccountAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'authorized',
        'show_auth_link',
    ]

admin.site.register(models.GoogleAccount, GoogleAccountAdmin)


class GoogleCalendarAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.GoogleCalendar, GoogleCalendarAdmin)
