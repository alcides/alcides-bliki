from datetime import timedelta
from elementtree.ElementTree import ElementTree
from urllib2 import urlopen

from django import template
from django.conf import settings


register = template.Library()

class Link(object):
	def __init__(self,node):
		self.url = node[1].text
		self.text = node[2].text
		self.before_text = node[3].text
		self.after_text = node[4].text

def tla_list(request):
    """
    """
    url = 'http://www.text-link-ads.com/xml.php?inventory_key=' + settings.TLA_INVENTORY_KEY + '&referer=' + request.META.get('REQUEST_URI', request.META.get('PATH_INFO', '/'))
    if 'HTTP_USER_AGENT' in request.META:
        agent = '&user_agent=' + request.META['HTTP_USER_AGENT']
    e = ElementTree()
    links = ElementTree.parse(e,urlopen(url+agent))
    return {
        'links': [ Link(link) for link in links ]
    }

register.inclusion_tag('tla/list.html')(tla_list)