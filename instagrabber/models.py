# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from taggit.managers import TaggableManager

class InstaUser(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.username

class InstaPicture(models.Model):
    instagram_id = models.CharField(max_length=100, unique=True)
    instagram_url = models.CharField(max_length=500)
    caption = models.TextField(default="")
    user = models.ForeignKey(InstaUser)
    likes = models.PositiveIntegerField(default=0)
    datetime = models.DateTimeField()
    tags = TaggableManager()

    selected = models.BooleanField(default=False)

    class Meta:
        ordering = ('-datetime',)
