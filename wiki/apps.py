from django.apps import AppConfig


class WikiAppConfig(AppConfig):
	name = 'wiki'

	def ready(self):
		from django.db.models.signals import pre_save

		from wiki.models import Page
		from wiki.signals import pre_save as pre_save_handler

		pre_save.connect(pre_save_handler, sender=Page)
