from django.db.models import Max

from wiki.models import Page, PageVersion

def pre_save(instance, **kwargs):
  if kwargs["sender"] == Page:
    original = Page.objects.get(id=instance.id)
    if instance.text != original.text:
      if PageVersion.objects.filter(page=original).count() > 0:
        version = PageVersion.objects.filter(page=original).aggregate(Max('version'))['version__max'] + 1
      else:
        version = 1
      PageVersion.objects.create(page=original, text=original.text, version=version)
