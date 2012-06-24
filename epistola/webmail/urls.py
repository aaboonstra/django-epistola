# vim: set syn=python ts=4 sw=4 sts=4 et ai:
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from epistola.webmail.views import MailView, ComposeMailView


urlpatterns = patterns('',
    url(r'^$', login_required(MailView.as_view()), name='webmail_view'),
    url(r'^compose/$', login_required(ComposeMailView.as_view()),
        name='webmail_compose'),
)
