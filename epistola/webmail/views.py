# vim: set syn=python ts=4 sw=4 sts=4 et ai:
import email
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, FormView, ListView 
from epistola.decorators import json_response 
from epistola.webmail.forms import SendMailForm
from epistola.imaplib_utils import open_imap_connection, parse_list


class MailView(TemplateView):
    template_name = 'webmail/mailview.html'

    def get_context_data(self, *args, **kwargs):
        context = super(MailView, self).get_context_data(*args, **kwargs)
        conn = open_imap_connection(self.request)
        type, data = conn.list()
        conn.logout()
        tree = parse_list(data)
        context.update({
            'folders': tree,
        })
        return context


class MailboxView(ListView):
    template_name = 'webmail/mailbox_detail.html'
    paginate_by = 50 
    mailbox = 'INBOX' # Default to INBOX
    conn = None

    def get_mailbox(self):
        try:
            self.mailbox = self.request.GET.get('mailbox')
        except:
            pass
        return self.mailbox

    def get_queryset(self):
        # Grab the msg count and the msg ids from the mailserver
        self.conn = open_imap_connection(self.request)
        type, msg_total = self.conn.select(str(self.get_mailbox()))
        type, msg_ids = self.conn.search(None, 'ALL')

        # Split the ids into an iterable list
        msg_ids_list = msg_ids[0].split()
        # reverse it so the new older messages end up at the end
        # of the list
        msg_ids_list.reverse()
        return msg_total, msg_ids_list 

    @method_decorator(json_response)
    def get(self, request, *args, **kwargs):
        msg_total, object_list = self.get_queryset()
        context = self.get_context_data(object_list=object_list,
                current_mailbox=self.mailbox)
        
        # Grab the paginated msg ids
        msg_ids_list = context['object_list']
        data = []
        if msg_ids_list:
            type, msg_data = self.conn.fetch(
                    '%s:%s' % (msg_ids_list[-1], msg_ids_list[0]),
                    '(BODY.PEEK[HEADER] FLAGS)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    data.append(email.message_from_string(response_part[1]))
            context.update({
                'msg_total': msg_total[0],
                'msg_first': msg_ids_list[-1],
                'msg_last': msg_ids_list[0],
            })
        self.conn.logout()
        context.update({
            'object_list': data,
        })
        resp =  render_to_string(self.template_name, context,
                context_instance=RequestContext(self.request))
        return {'status': 'success', 'redirect': None, 'html': resp}


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
        resp = render_to_string('webmail/compose_mail.html',
                self.get_context_data(form=form),
                context_instance=RequestContext(self.request))
        return {'status': 'error', 'redirect': None, 'html': resp}
