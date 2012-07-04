# vim: set syn=python ts=4 sw=4 sts=4 et ai:
import mimetypes
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from epistola.attachment.models import Attachment, DocumentType

BLOCKED_MIMETYPES = getattr(settings, 'ATTACHMENT_BLOCKED_MIMETYPES', ())
ALLOWED_MIMETYPES = getattr(settings, 'ATTACHMENT_ALLOWED_MIMETYPES', ())


class CreateAttachmentForm(forms.ModelForm):
    '''
    Create an attachment for a group and user.
    '''
    f = forms.FileField()

    class Meta:
        model = Attachment
        fields = ('f',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CreateAttachmentForm, self).__init__(*args, **kwargs)

    def clean(self):
        file = self.cleaned_data.get('f')
        # content_type is set by the upload handler based on file extension
        content_type = file.content_type
        if not content_type:
            raise forms.ValidationError(_('Cannot determine the content type ' \
                'of the given file: %s.') % file.name)
        for mime_type in ALLOWED_MIMETYPES:
            if content_type.startswith(mime_type.replace('*', '')):
                break
        else:
            raise forms.ValidationError(_('It is not allowed to' \
                'upload "%s" files.') % file.name)

        for mime_type in BLOCKED_MIMETYPES:
            if content_type.startswith(mime_type):
                raise forms.ValidationError(_('It is not allowed to' \
                        'upload "%s" files.') % file.name)
        return self.cleaned_data

    def save(self, commit=True):
        file = self.cleaned_data.get('f')
        object = super(CreateAttachmentForm, self).save(commit=False)
        object.user = self.user
        content_type = file.content_type
        # This if statement might look strange but it will
        # make sence in the future
        if content_type is None:
            object.object = self.create_document(file)
        else:
            object.object = self.create_document(file)

        if commit:
            object.save()
            self.save_m2m()
        return object

    def create_document(self, file):
        ct, enc = mimetypes.guess_type(file.name)
        filetype = ct.split('/')[1]
        if filetype == 'vnd.openxmlformats-officedocument.wordprocessingml.document': # A shorter name would be nice so we dont spam the overview template
            filetype = 'docx' # that'll work...
        if filetype == 'vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            filetype == 'xlsx'
        if filetype == 'vnd.openxmlformats-officedocument.presentationml.presentation':
            filetype == 'pptx'

        return DocumentType.objects.create(document=file, user=self.user,
                filetype=filetype)
