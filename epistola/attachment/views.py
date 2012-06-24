# vim: set ts=8 sw=4 sts=4 et ai:
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.generic import FormView
from epistola.attachment.forms import CreateAttachmentForm
from epistola.decorators import json_response
from epistola.uploadhandler import AjaxMemoryFileUploadHandler, \
    AjaxTemporaryFileUploadHandler

class AttachmentUploadView(FormView):
    def get_form(self, form):
        form = CreateAttachmentForm(files=self.request.FILES,
            user=self.request.user)
        return form 

    @method_decorator(csrf_exempt)
    @method_decorator(json_response)
    def dispatch(self, request, *args, **kwargs):
        request.upload_handlers = [AjaxMemoryFileUploadHandler(),
            AjaxTemporaryFileUploadHandler()]
        return csrf_protect(super(AttachmentUploadView, self).dispatch)(request,
                *args, **kwargs)

    def get(self, *args, **kwargs):
        return {'error': 'Invalid request'}

    def form_valid(self, form):
        object = form.save()
        return {'success': True, 'url': object.id}

    def form_invalid(self, form):
        return {'error': unicode(
            form.non_field_errors())}
