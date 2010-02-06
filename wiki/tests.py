import string
from random import choice
import unittest

from django.template.defaultfilters import slugify
from django.test import TestCase, Client
from django.contrib.auth.models import User

from wiki.models import *

class PageTestCase(unittest.TestCase):
  
  def randomTitle(self, size = 10):
    chars = string.digits + string.letters + " .-_+?!"
    return "".join([ choice(chars) for i in range(size)])
  
  def setUp(self):
    self.u =  User.objects.create_user("jsmith", "jsmith@example.com", "test123")
    self.l = Language.objects.create(name="Portuguese",code="pt-PT")
    self.t = self.randomTitle() 
    self.slug = slugify(self.t)
    self.c = Page.objects.create(
      title = self.t,
      slug = self.slug,
      author = self.u,
      lang = self.l,
      text = "whatever"
    )
    
  def tearDown(self):
    self.u.delete()
    self.l.delete()
    PageVersion.objects.filter( id=self.c.id ).delete()
    self.c.delete()
    
  def testVersioning(self):
    def iter(i):
      self.count_before = PageVersion.objects.filter(page__id=self.c.id).count()
      self.c.text = "after whatever %d" % i 
      self.c.save()
      self.count_after = PageVersion.objects.filter(page__id=self.c.id).count()
      self.assertEquals(self.count_before + 1, self.count_after)
    for i in range(5):
      iter(i)
    
  def testPageIsViewed(self):
    c = Client()
    response = c.get("/%s" % self.slug)
    self.failUnlessEqual(response.status_code, 301)
    response = c.get("/%s/" % self.slug)    
    self.failUnlessEqual(response.status_code, 200)    