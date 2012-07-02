# vim: set ts=8 sw=4 sts=4 et ai:
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class EpistolaAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(EpistolaAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = _('E-mail address')

    def clean_username(self):
        return self.cleaned_data['username'].lower()

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            key = ('failed_login_for_%s_%s' % (self.request.META['REMOTE_ADDR'], username))
            cache.add(key, 0, settings.FAILED_LOGIN_TIMEOUT)
            failed_attempts = cache.get(key)
            if failed_attempts >= settings.FAILED_LOGIN_ATTEMPT_LIMIT:
                raise forms.ValidationError(_('Failed login limit reached! Please try again in 5 minutes...'))
            else:
                self.user_cache = authenticate(username=username, password=password)
                if self.user_cache is None:
                    cache.incr(key)
                    raise forms.ValidationError(_('Please enter a correct username and password. The password is case sensitive.'))
                elif not self.user_cache.is_active:
                    raise forms.ValidationError(_('This account is inactive.'))
            if failed_attempts:
                cache.delete(key)
            self.request.session['password'] = password
        self.check_for_test_cookie()
        return self.cleaned_data

