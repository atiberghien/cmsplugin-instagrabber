# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-22 10:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instagrabber', '0007_instaconfig_backlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instaconfig',
            name='password',
        ),
        migrations.RemoveField(
            model_name='instaconfig',
            name='username',
        ),
    ]
