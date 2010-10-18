"""CategoryAdmin for Zinnia"""
from django.contrib import admin

from frinat.sponsors import models

class SponsorAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Sponsor, SponsorAdmin)

