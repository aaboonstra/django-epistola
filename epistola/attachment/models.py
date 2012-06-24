# vim: set syn=python ts=4 sw=4 sts=4 et ai:
from os import path
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db import models
from epistola.models import AbstractModel as Model 


def get_attachment_media_path(instance, filename):
    return path.join('attachments', str(instance.user.username), filename)

class Attachment(Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.CharField(_('object id'), db_index=True, max_length=24)
    object = generic.GenericForeignKey('content_type', 'object_id')


class DocumentType(Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    document = models.FileField(upload_to=get_attachment_media_path)
    filetype = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = path.basename(self.document.name)
        super(DocumentType, self).save(*args, **kwargs)
