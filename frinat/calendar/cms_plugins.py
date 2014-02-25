from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from frinat.calendar import models, periods
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
import datetime


class CMSCalendarMonthPlugin(CMSPluginBase):
    model = models.MonthCalendarPlugin
    name = _("Monthly calendar (deprecated)")
    render_template = "calendar/month-deprecated.html"

    def render(self, context, instance, placeholder):
        from schedule.conf.settings import GET_EVENTS_FUNC
        from schedule.periods import Month, weekday_names

        date = context.get('date', datetime.datetime.now())

        event_list = []
        for calendar in instance.calendars_to_display.all():
            event_list += GET_EVENTS_FUNC(context['request'], calendar)

        period = Month(event_list, date)

        context.update({
            'date': date,
            'events': event_list,
            'period': period,
            'calendar': instance.calendars_to_display.all(),
            'weekday_names': weekday_names,
            'display_details': instance.display_details,
        })

        return context

plugin_pool.register_plugin(CMSCalendarMonthPlugin)


class CMSGoogleCalendarPlugin(CMSPluginBase):
    model = models.GoogleCalendarPlugin
    name = _("Google calendar")
    render_template = "calendar/month.html"

    def render(self, context, instance, placeholder):
        from schedule.periods import weekday_names

        date = context.get('date', now())

        event_list = []
        period = periods.Month.fordate(date, [])
        for calendar in instance.calendars_to_display.all():
            event_list += calendar.get_events(period.start, period.end)
        period = periods.Month.fordate(date, event_list)

        context.update({
            'date': date,
            'events': event_list,
            'month': period,
            'calendar': instance.calendars_to_display.all(),
            #'weekday_names': weekday_names,
            'display_details': True,
        })

        return context

plugin_pool.register_plugin(CMSGoogleCalendarPlugin)
