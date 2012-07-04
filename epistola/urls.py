# vim: set syn=python ts=4 sw=4 sts=4 et ai:
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to
admin.autodiscover()
from epistola.forms import EpistolaAuthenticationForm

urlpatterns = patterns('',
    
    # Management
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/login/', 'django.contrib.auth.views.login',{
        'template_name': 'registration/login.html',
        'authentication_form': EpistolaAuthenticationForm}, name='login'),
    url(r'^account/logout/','django.contrib.auth.views.logout_then_login',
        name='logout'),

    (r'^$', redirect_to, {'url': '/webmail/'}),

    # Webmail contents
    (r'^webmail/', include('epistola.webmail.urls', namespace='webmail')),
    (r'^attachment/', include('epistola.attachment.urls',
        namespace='attachment')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
