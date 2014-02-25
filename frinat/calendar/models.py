from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.timezone import utc

import httplib2
from cms.models import CMSPlugin
from schedule.models import Calendar
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import CredentialsField, Storage
from apiclient.discovery import build

from dateutil import parser, tz

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^oauth2client\.django_orm\.CredentialsField"])


class Event(object):
    NORMAL, ALL_DAY = range(2)

    def __init__(self, calendar, data):
        self.calendar = calendar
        self._data = data
        self.data = data
        self.id = data['id']
        self.title = data['summary']
        self.location = data.get('location', None)
        self.description = data.get('description', None)

        if 'date' in data['start']:
            # Whole day
            self.kind = Event.ALL_DAY
            start = parser.parse(data['start']['date']).replace(tzinfo=utc)
            end = parser.parse(data['end']['date']).replace(tzinfo=utc)
            tz_start = settings.TIME_ZONE
            tz_end = settings.TIME_ZONE
        else:
            self.kind = Event.NORMAL
            start = parser.parse(data['start']['dateTime'])
            end = parser.parse(data['end']['dateTime'])
            tz_start = data['start'].get('timeZone', settings.TIME_ZONE)
            tz_end = data['end'].get('timeZone', settings.TIME_ZONE)

        tz_start = tz.gettz(tz_start)
        tz_end = tz.gettz(tz_end)

        start = start.replace(tzinfo=tz_start)
        end = end.replace(tzinfo=tz_end)

        self.start = start
        self.end = end

    def __eq__(self, other):
        return self.id == other.id

    def isallday(self):
        return self.kind == Event.ALL_DAY


class GoogleAccount(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def get_flow(self, request):
        path = reverse('calendar_oauth:callback')
        url = request.build_absolute_uri(path)
        return OAuth2WebServerFlow(settings.GOOGLE_API_ID,
                                   settings.GOOGLE_API_SECRET,
                                   'https://www.googleapis.com/auth/calendar',
                                   url)

    @property
    def credentials(self):
        storage = Storage(Credentials, 'id', self, 'credentials')
        return storage.get()

    @credentials.setter
    def credentials(self, cred):
        storage = Storage(Credentials, 'id', self, 'credentials')
        storage.put(cred)

    def authorized(self):
        return (self.credentials is not None and
                self.credentials.invalid == False and
                not self.credentials.access_token_expired)
    authorized.boolean = True

    def show_auth_link(self):
        return '<a href="{}">Authorize</a>'.format(reverse(
            'calendar_oauth:authorize', kwargs={'account_id': self.pk}))
    show_auth_link.allow_tags = True
    show_auth_link.short_description = 'Authorization link'


class Credentials(models.Model):
    id = models.OneToOneField(GoogleAccount, primary_key=True,
                              related_name='_credentials')
    credentials = CredentialsField(editable=False)


class GoogleCalendar(models.Model):
    calendar_id = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    account = models.ForeignKey(GoogleAccount, null=False, blank=False)

    def __unicode__(self):
        return u'{} (on {})'.format(self.name, self.account.name)

    def get_events(self, start=None, end=None):
        credentials = self.account.credentials

        kwargs = {}

        if start is not None:
            kwargs['timeMin'] = start.isoformat()

        if end is not None:
            kwargs['timeMax'] = end.isoformat()

        http = httplib2.Http()
        http = credentials.authorize(http)

        service = build('calendar', 'v3', http=http)
        events = service.events().list(
            calendarId=self.calendar_id,
            singleEvents=True,
            orderBy='startTime',
            showDeleted=False,
            timeZone=settings.TIME_ZONE,
            **kwargs
        ).execute()
        events = events['items']
        for e in events:
            if e['status'] == 'confirmed':
                yield Event(self, e)


class GoogleCalendarPlugin(CMSPlugin):
    calendars_to_display = models.ManyToManyField(GoogleCalendar)

    def copy_relations(self, oldinstance):
        self.calendars_to_display = oldinstance.calendars_to_display.all()


class MonthCalendarPlugin(CMSPlugin):
    calendars_to_display = models.ManyToManyField(Calendar)
    display_details = models.BooleanField(default=True)

    def copy_relations(self, oldinstance):
        self.calendars_to_display = oldinstance.calendars_to_display.all()
