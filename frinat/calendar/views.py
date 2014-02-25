import datetime

from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse
from oauth2client.django_orm import Storage
from oauth2client import xsrfutil
from schedule.periods import weekday_names
from dateutil.tz import gettz

from . import models


def month(request, year=0, month=0):
    year = int(year)
    month = int(month)

    if not year:
        year = datetime.datetime.today().year

    if not month:
        month = datetime.datetime.today().month

    date = datetime.datetime(year, month, 1, tzinfo=gettz(settings.TIME_ZONE))

    return render_to_response('left-sidebar.html', {
        'date': date,
        'weekday_names': weekday_names,
        'managed': True,
    }, context_instance=RequestContext(request))


def authorize(request, account_id):
    account = get_object_or_404(models.GoogleAccount, pk=int(account_id))
    credentials = account.credentials

    if credentials is None or credentials.invalid == True:
        flow = account.get_flow(request)
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        authorize_url = flow.step1_get_authorize_url()
        request.session['google_account_id'] = account.pk
        return HttpResponseRedirect(authorize_url)
    else:
        return HttpResponseRedirect(reverse(
            'admin:calendar_googleaccount_changelist'))


def auth_return(request):
    account_id = request.session.get('google_account_id', None)

    if account_id is None:
        return HttpResponseBadRequest()

    if not xsrfutil.validate_token(settings.SECRET_KEY,
                                   request.REQUEST['state'],
                                   request.user):
        return HttpResponseBadRequest()

    account = get_object_or_404(models.GoogleAccount, pk=int(account_id))
    flow = account.get_flow(request)
    credentials = flow.step2_exchange(request.REQUEST)
    account.credentials = credentials
    account.save()
    return HttpResponseRedirect(reverse(
        'admin:calendar_googleaccount_changelist'))
