from dateutil.relativedelta import relativedelta, MO


class EventsManager(object):
    def __init__(self, events):
        self.events_start = sorted(events, key=lambda x: x.start)

    def in_period(self, period):
        for e in self.events_start:
            if e.start >= period.end:
                break
            if e.end <= period.start:
                continue
            yield Occurrence(period, e)
        return


class Occurrence(object):
    def __init__(self, period, event):
        self.event = event
        self.period = period

    def starts(self):
        return (self.event.start >= self.period.start and
                self.event.start < self.period.end)

    def ends(self):
        return (self.event.end > self.period.start and
                self.event.end <= self.period.end)

    def contained(self):
        return self.starts() and self.ends()

    def spans(self):
        return (self.event.start < self.period.start and
                self.event.end > self.period.end)


class Period(object):
    def __init__(self, start, end, events):
        self.start = start
        self.end = end
        if not isinstance(events, EventsManager):
            events = EventsManager(events)
        self.events_manager = events

    @classmethod
    def fordate(cls, date, events):
        start = cls._start_for_date(date)
        end = cls._end_for_date(date)
        return cls(start, end, events)

    def iterperiods(self, period_cls):
        period = period_cls.fordate(self.start, self.events_manager)
        while True:
            yield period
            if period.end >= self.end:
                break
            period = period.next_period()

    def next_period(self):
        return self.__class__.fordate(self.end, self.events_manager)

    def prev_period(self):
        return self.__class__.fordate(self.start - relativedelta(seconds=1),
                                      self.events_manager)

    def has_events(self):
        return any(self.events())

    def events(self):
        return self.events_manager.in_period(self)


class Month(Period):
    @classmethod
    def _start_for_date(cls, date):
        return date.replace(day=1, hour=0, minute=0, second=0,
                            microsecond=0)

    @classmethod
    def _end_for_date(cls, date):
        return cls._start_for_date(date) + relativedelta(months=1)

    def weeks(self):
        return self.iterperiods(Week)


class Week(Period):
    @classmethod
    def _start_for_date(cls, date):
        day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day += relativedelta(weekday=MO(-1))
        return day

    @classmethod
    def _end_for_date(cls, date):
        return cls._start_for_date(date) + relativedelta(days=7)

    def days(self):
        return self.iterperiods(Day)


class Day(Period):
    @classmethod
    def _start_for_date(cls, date):
        day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        return day

    @classmethod
    def _end_for_date(cls, date):
        return cls._start_for_date(date) + relativedelta(days=1)
