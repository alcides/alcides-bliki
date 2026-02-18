from datetime import datetime
from django.contrib import admin
from wiki.models import ImageUpload, Language, Page, PageVersion, Tag
	
def publish(modeladmin, req, qs):
  qs.update(pubdate=datetime.now())
	
class TagAdmin(admin.ModelAdmin):
	search_fields = ['name', 'slug']
	prepopulated_fields = {'slug': ('name',)}


class PageAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("title",)}
	search_fields = ['slug','title','text']
	list_filter = ('lang','pubdate', 'date', 'author')
	list_display = ('title','slug','is_published','date','lang')
	list_display_links = ('title', 'slug')
	autocomplete_fields = ['tags']
	
	fieldsets = (
	        ('Content', {
	            'fields': ('title', 'text')
	        }),
	        ('Meta', {
	            'fields': ('slug','lang', 'pubdate', 'author', 'tags')
	        }),
	    )
	
	save_on_top = True
	actions = [publish]
	
	
def restore_version(modeladmin, req, qs):
  for o in qs:
    p = o.page
    p.text = o.text
    p.save()
	
class PageVersionAdmin(admin.ModelAdmin):
  list_display = ('page','version')
  actions = [restore_version]

admin.site.register(Language)
admin.site.register(Tag, TagAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(PageVersion, PageVersionAdmin)
admin.site.register(ImageUpload)