from cms.sitemaps import CMSSitemap
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {
        'sitemaps': {
            'cmspages': CMSSitemap
        },
    }),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^calendar/accounts/', include('frinat.calendar.urls.oauth',
                                        namespace='calendar_oauth',
                                        app_name='calendar_oauth')),
    url(r'^', include('cms.urls')),
)

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ) + urlpatterns

if settings.MEDIA_DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ) + urlpatterns

if settings.STATICFILES_DEBUG:
    urlpatterns = patterns('',
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
