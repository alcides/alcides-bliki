from django.contrib import admin
from wiki.models import Language, Page, PageVersion
	
class PageAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("title",)}
	search_fields = ['slug','title','text']
	list_filter = ('lang','pubdate', 'date', 'author')
	list_display = ('title','slug','is_published','date','lang')
	list_display_links = ('title', 'slug')
	
	fieldsets = (
	        ('Content', {
	            'fields': ('title', 'text')
	        }),
	        ('Meta', {
	            'fields': ('slug','lang', 'pubdate', 'author')
	        }),
	    )
	
	save_on_top = True
	
	
def restore_version(modeladmin, req, qs):
  for o in qs:
    p = o.page
    p.text = o.text
    p.save()
	
class PageVersionAdmin(admin.ModelAdmin):
  list_display = ('page','version')
  actions = [restore_version]

admin.site.register(Language)
admin.site.register(Page, PageAdmin)
admin.site.register(PageVersion, PageVersionAdmin)