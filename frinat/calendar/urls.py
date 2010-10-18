from django.conf.urls.defaults import *
 
urlpatterns = patterns('frinat.calendar.views',
    url(r'^$', 'month', name='current_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{2})/$', 'month', name='single_month'),
)
