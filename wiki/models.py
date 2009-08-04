from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Language(models.Model):
	name =  models.CharField(blank=True, max_length=100)
	code = models.CharField(blank=True, max_length=10)
		
	def __unicode__(self):
		return u'%s' % (self.name)

class Page(models.Model):
	title = models.CharField(blank=True, max_length=180)
	slug = models.CharField(max_length=60)
	lang = models.ForeignKey(Language)
	pubdate = models.DateTimeField(blank=True,null=True)
	date = models.DateTimeField(auto_now=True)
	author = models.ForeignKey(User)
	text = models.TextField()
	

	class Meta:
		ordering = ['-date']
		get_latest_by = "date"
		
	def __unicode__(self):
		return u'%s' % (self.title)
	
	def get_absolute_url(self):
		return "/%s/" % self.slug
		
	def is_published(self):
		return self.pubdate != None
	is_published.short_description = 'Published?'
	is_published.boolean = True

if not settings.DEBUG or 1:
	from django.db.models.signals import pre_save, pre_delete
	from staticgenerator import quick_delete

	def delete_cache(sender, instance, **kwargs):
		   quick_delete(instance, '/')
		
	pre_save.connect(delete_cache,sender=Page)
	pre_delete.connect(delete_cache,sender=Page)