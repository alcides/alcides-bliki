from datetime import timedelta
from elementtree.ElementTree import ElementTree
from urllib import urlopen

from django import template
from django.conf import settings


register = template.Library()


def tla_list(request):
    """
    """
    url = 'http://www.text-link-ads.com/xml.php?inventory_key=' + settings.TLA_INVENTORY_KEY + '&referer=' + request.META.get('REQUEST_URI', request.META.get('PATH_INFO', '/'))
    agent = '&user_agent=' + request.META['HTTP_USER_AGENT']
    links = ElementTree.parse(urlopen(url+agent)).getroot()
    
    return {
        'links': links
    }
    
    # This is here so I don't forget it. :P
    # Don't know which way really works yet.
    #
    # return {
    #     'links': {
    #         'after_text': links.find('after_text').text,
    #         'before_text': links.find('before_text').text,
    #         'text': links.find('text').text,
    #         'url': links.find('url').text,
    #     }
    # }

register.inclusion_tag('templates/tla/list.html')(tla_list)