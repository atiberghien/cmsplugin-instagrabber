# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from .models import InstaUser, InstaPicture, InstaConfig

class SingletonModelAdmin(admin.ModelAdmin):
    actions = None 

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return InstaConfig.objects.count() == 0

class InstaConfigForm(forms.ModelForm):
    class Meta:
        model = InstaConfig
        fields = "__all__"
        widgets = {
            'password': forms.PasswordInput(),
        }

@admin.register(InstaConfig)
class InstaConfigAdmin(SingletonModelAdmin):
    form = InstaConfigForm

@admin.register(InstaUser)
class InstaUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username')


from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
class ImageUrlWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        forms.TextInput.render(self, name, value, attrs)
        flat_attrs = flatatt(attrs)
        html = '<img src="%s" width="300" height="300"/>' % value
        return mark_safe(html)

class InstaPictureForm(forms.ModelForm):
    class Meta:
        model = InstaPicture
        widgets = {
            'instagram_url': ImageUrlWidget(),
        }
        exclude = ('instagram_id',)

@admin.register(InstaPicture)
class InstaPictureAdmin(admin.ModelAdmin):
    list_display = ('id',   'image_img', 'selected', 'likes', 'user','datetime' )
    list_editable = ('selected', )
    form = InstaPictureForm
    fieldsets = (
        (None, {
            'fields': (('instagram_url', 'caption'),
                        ('user', 'datetime'),
                        ('likes', 'tags'))
        }),
    )
    readonly_fields = ['caption', 'user', 'datetime','likes', 'tags']

    class Media:
        js = (
            'jquery/dist/jquery.slim.min.js',
            'tooltipster/dist/js/tooltipster.bundle.min.js',
            'js/admin/instagrabber.js',
        )    
        css = {
            'all': (
                'tooltipster/dist/css/tooltipster.bundle.min.css',
                'css/admin/instagrabber.css',
            )
        }

    def image_img(self, obj):
        return u'<img class="instagram-picture" src="%s" width="150" height="150" title="%s"/>' % (obj.instagram_url, obj.caption)
    image_img.short_description = 'Image'
    image_img.allow_tags = True