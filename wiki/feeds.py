from django.contrib.syndication.views import Feed
from .models import Page, Language

import datetime

NUMBER_OF_ITEMS = 10

class WikiFeed(Feed):
    link = "/"
    description = "A Maelstrom of Ideas, Code and Politics"
    title_template = 'feeds/title.html'
    description_template = 'feeds/description.html'

    def item_link(self, obj):
        return "/%s" % obj.slug
        
    def item_title(self, obj):
        return "%s" % obj.title
        
    def item_description(self,obj):
        return "%s" % obj.text
        
    def item_author_name(self, obj):
        return "%s" % obj.author.username
        
    def item_author_email(self,obj):
        return "%s" % obj.author.email

    def item_pubdate(self, obj):
        return obj.pubdate


class English(WikiFeed):
    title = "Alcides Fonseca (english feed)"

    def items(self):
        en = Language.objects.get(code="en")
        return Page.objects.filter(lang=en).exclude(pubdate=None).exclude(pub_date__gte=datetime.date.today()).order_by('-pubdate')[:NUMBER_OF_ITEMS]

        
class Portuguese(WikiFeed):
    title = "Alcides Fonseca (feed em Portugues)"

    def items(self):
        pt = Language.objects.get(code="pt")
        return Page.objects.filter(lang=pt).exclude(pubdate=None).exclude(pub_date__gte=datetime.date.today()).order_by('-pubdate')[:NUMBER_OF_ITEMS]

        
class All(WikiFeed):
    title = "Alcides Fonseca"

    def items(self):
        return Page.objects.exclude(pubdate=None).exclude(pub_date__gte=datetime.date.today()).order_by('-pubdate')[:NUMBER_OF_ITEMS]
