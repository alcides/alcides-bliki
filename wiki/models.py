from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse

class Language(models.Model):
	name =  models.CharField(blank=True, max_length=100)
	code = models.CharField(blank=True, max_length=10)
		
	def __str__(self):
		return f'{self.name}'

class Tag(models.Model):
	name = models.CharField(max_length=60)
	slug = models.SlugField(max_length=60, unique=True)

	def __str__(self):
		return self.name


class Page(models.Model):
	title = models.CharField(blank=True, max_length=180)
	slug = models.CharField(max_length=60)
	lang = models.ForeignKey(Language, on_delete=models.CASCADE)
	pubdate = models.DateTimeField(blank=True,null=True)
	date = models.DateTimeField(auto_now=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.TextField()
	tags = models.ManyToManyField(Tag, blank=True, related_name='pages')
	
	class Meta:
		ordering = ['-date']
		get_latest_by = "date"
		
	def __str__(self):
		return f'{self.title}'
	
	def get_absolute_url(self):
		return reverse("page_detail", kwargs={"slug": self.slug})
		
	def is_published(self):
		return self.pubdate != None

	is_published.short_description = 'Published?'
	is_published.boolean = True

class PageVersion(models.Model):
	page = models.ForeignKey(Page, on_delete=models.CASCADE)
	version = models.IntegerField()
	text = models.TextField()
	
	def __str__(self):
		return f"{self.page.title} v{self.version}"
	

class ImageUpload(models.Model):
	image = models.ImageField(upload_to="images")

	def __str__(self):
		return f"{self.image}"
