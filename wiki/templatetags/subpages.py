from wiki.models import Page
from django.template import Library,Node, resolve_variable

register = Library()

# use for tag cloud
def show_subpages(parser, token):
    """ {% get_subpages page.slug %}"""
    try:
        tag_name, page_slug = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires exactly one arguments" % token.contents.split()[0]
    return SubpageListObject(page_slug)

class SubpageListObject(Node):
    def __init__(self,slug):
        self.slug = slug

    def render(self, context): 
        context['subpages'] = Page.objects.filter(slug__startswith=str(resolve_variable(self.slug,context))+"/")
        return ''

register.tag('get_subpages', show_subpages)