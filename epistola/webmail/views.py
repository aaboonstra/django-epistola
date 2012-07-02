# vim: set syn=python ts=4 sw=4 sts=4 et ai:
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, FormView
from epistola.decorators import json_response 
from epistola.webmail.forms import SendMailForm
from epistola.imaplib_utils import open_connection, parse_list


class MailView(TemplateView):
    template_name = 'webmail/mailview.html'

    def get_context_data(self, *args, **kwargs):
        context = super(MailView, self).get_context_data(*args, **kwargs)
        conn = open_connection(self.request)
        type, data = conn.list()
        tree = parse_list(data)
        conn.logout()

        context.update({
            'folders': tree,
        })
        return context


class ComposeMailView(FormView):
    form_class = SendMailForm 
    template_name = 'webmail/compose_mail.html'

    @method_decorator(json_response)
    def form_valid(self, form):
        message = _("Email sent succesfully")
        messages.add_message(self.request, messages.SUCCESS, unicode(message))
        redirect = reverse('webmail:webmail_view') 
        return {'status': 'success', 'redirect': redirect}

    @method_decorator(json_response)
    def form_invalid(self, form):
        r = render_to_string('webmail/compose_mail.html', self.get_context_data(
            form=form), context_instance=RequestContext(self.request))
        return {'status': 'error', 'redirect': None, 'html': r}
