from django.contrib import admin
from wiki.models import Language, Page

class LanguageAdmin(admin.ModelAdmin):
	pass
	
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
	

admin.site.register(Language, LanguageAdmin)
admin.site.register(Page,PageAdmin)