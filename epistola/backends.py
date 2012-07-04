# vim: set syn=python ts=4 sw=4 sts=4 et ai:
# Based on http://www.djangorocks.com/tutorials/creating-a-custom-authentication-backend/creating-the-imap-authentication-backend.html
from django.conf import settings
from django.contrib.auth.models import User
from imapclient import IMAPClient

class ImapAuthenticationBackend(object):

    # Create an authentication method
    # This is called by the standard Django login procedure
    def authenticate(self, username=None, password=None):
        try:
            # Check if this user is valid on the mail server
            c = IMAPClient(settings.MAIL_SERVER, use_uid=True,
                    ssl=settings.USE_SSL)
            c.login(username, password)
            c.logout()
        except:
            return None

        try:
            # Check if the user exists in Django's local database
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Create a user in Django's local database
            user = User.objects.create_user(username, email=username,
                    password=password)

        return user

    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
