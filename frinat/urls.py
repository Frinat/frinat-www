from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^news/', include('zinnia.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
)

if settings.DEBUG:
    import os
    import cms
    import zinnia
    
    media = (
        (settings.ADMIN_MEDIA_PREFIX, os.path.join(os.path.dirname(admin.__file__), 'media')),
        (settings.MEDIA_URL + 'cms/', os.path.join(os.path.dirname(cms.__file__), 'media', 'cms')),
        (settings.ZINNIA_MEDIA_URL, os.path.join(os.path.dirname(zinnia.__file__), 'media', 'zinnia')),
        (settings.MEDIA_URL, settings.MEDIA_ROOT),
    )
    
    murl = lambda u, r: url(r'^%s(?P<path>.*)$' % u[1:], 'django.views.static.serve', {
        'document_root': r,
        'show_indexes': True,
    })
    
    urlpatterns += patterns('', *[murl(*u) for u in media])

urlpatterns += patterns('',
    url(r'^', include('cms.urls')),
)