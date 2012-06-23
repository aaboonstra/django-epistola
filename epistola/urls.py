from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()

from epistola.views import HomeView

urlpatterns = patterns('',
    
    # Management
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/login/', 'django.contrib.auth.views.login', name='login'),
    url(r'^account/logout/','django.contrib.auth.views.logout_then_login' , name='logout'),

    # Webmail contents
    url(r'^$', login_required(HomeView.as_view()), name='home'),
)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
