from django.conf.urls import patterns, url


urlpatterns = patterns('frinat.calendar.views',
    url(r'^(?P<account_id>\d+)/authorize/$', 'authorize', name='authorize'),
    url(r'^callback/$', 'auth_return',
        name='callback'),
)
