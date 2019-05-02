# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from .models import InstaPicture


@plugin_pool.register_plugin
class InstagramWall(CMSPluginBase):
    name = _(u"Social Wall Instagram")
    render_template = "instagrabber/wall.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = CMSPluginBase.render(self, context, instance, placeholder)
        context["posts"] = InstaPicture.objects.filter(selected=True)
        return context