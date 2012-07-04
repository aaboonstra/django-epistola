# vim: set ts=4 sw=4 sts=4 et ai:
from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from epistola.attachment.views import AttachmentUploadView 

urlpatterns = patterns('', 
    url(r'^(?P<pk>[^/]+)/$', login_required(AttachmentUploadView.as_view()),
        name='create'),
)
