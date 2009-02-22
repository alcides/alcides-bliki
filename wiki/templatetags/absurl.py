from django import template
from django.contrib.sites.models import Site
from alcides import settings

register = template.Library()
 
@register.filter("absolute_urls")
def absolute_urls(value):
	import re
	p = re.compile(  r"(<a href=\"/)" )
	
	current_site = Site.objects.get(id=settings.SITE_ID)
	
	return p.sub("<a href=\"http://"+current_site.domain+"/",value)
