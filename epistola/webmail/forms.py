# vim: set syn=python ts=4 sw=4 sts=4 et ai:
from django import forms


class SendMailForm(forms.Form):
    mail_to = forms.CharField(label='To')
    mail_cc = forms.CharField(label='CC', required=False)
    mail_bcc = forms.CharField(label='BCC', required=False)
    mail_subject = forms.CharField(label='Subject', max_length='255')
    mail_body = forms.CharField(widget=forms.Textarea)
