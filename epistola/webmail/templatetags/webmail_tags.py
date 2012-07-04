# vim: set syn=python ts=4 sw=4 sts=4 et ai:
from django import template
register = template.Library()


class ParseFoldersNode(template.Node):
    def __init__(self, folders):
        self.folders = template.Variable(folders)

    def render(self, context):
        try:
            folders = self.folders.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        ParseFoldersNode.html = ''
        def parse(folders):
            ParseFoldersNode.html += '<ul>' 
            for k,v in folders.iteritems():
                if isinstance(v, dict) and v:
                    ParseFoldersNode.html += '<li><a data-lookup_name="%s" ' \
                        'href="javascript:;">%s</a></li>' % (k.lookup_name,
                        k.name)
                    parse(v)
                else:
                    ParseFoldersNode.html += '<li><a data-lookup_name="%s" ' \
                        'href="javascript:;">%s</a></li>' % (k.lookup_name,
                        k.name)
            ParseFoldersNode.html += '</ul>'

        parse(folders)
        return ParseFoldersNode.html


@register.tag
def parse_folders(parser, token):

    bits = list(token.split_contents())
    if not 1 < len(bits) < 3:
       raise template.TemplateSyntaxError("%r tag requires ' \
               'folders argument" % bits[0]) 

    return ParseFoldersNode(*bits[1:])


@register.filter(name='split')
def split(value, arg):
    return value.split('.')
