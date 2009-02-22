from django.shortcuts import render_to_response, get_object_or_404
from wiki.models import Page

def index(request):
	latest_pages = Page.objects.all().order_by('-pubdate')[:20]
	return render_to_response('index.html', {'latest_pages': latest_pages})

def page_detail(request,slug):
	p = get_object_or_404(Page,slug=slug)
	return render_to_response('page_detail.html', {'page': p})