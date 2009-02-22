from django.template import Library,Node

register = Library()

def load_delicious_links(parser, token):
    """
    {% get_user_profile %}
    """
    return DeliciousObject()

class DeliciousObject(Node):
    def render(self, context):
		
		try:
			import feedparser
			d = feedparser.parse('http://del.icio.us/rss/alcidesfonseca')
			delicious=[]
			for entry in d['entries'][:min(8,len(d['entries']))]:
				title=str(entry['title'].encode('ascii', 'xmlcharrefreplace'))
				delicious.append({'title':title,'link':str(entry['links'][0]['href'])})
		except:
			delicious=[]
	
		context['delicious_links'] = delicious
		return ""

register.tag('load_delicious_links', load_delicious_links)
