# vim: set syn=python ts=4 sw=4 sts=4 et ai:
from django.db import models


class AbstractModel(models.Model):
    '''
    Abstract model implemantion with extended functionality
    of the django model class
    '''
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True
