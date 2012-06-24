from django import template
from epistola.attachment.forms import ALLOWED_MIMETYPES
register = template.Library()


@register.simple_tag
def get_allowed_attachment_mimetypes():
    return ','.join(ALLOWED_MIMETYPES)
