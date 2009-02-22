from django.contrib import admin
from wiki.models import Language, Page

class LanguageAdmin(admin.ModelAdmin):
	pass
	
class PageAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("title",)}
	search_fields = ['slug','title','text']
	list_filter = ('pubdate', 'date', 'author','lang')
	list_fields = ('title','slud','date','pub_date','lang')

admin.site.register(Language, LanguageAdmin)
admin.site.register(Page,PageAdmin)