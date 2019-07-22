# -*- coding: utf-8 -*-
import fnmatch
import hashlib
import json
import os
import re
import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from datetime import datetime
from bs4 import BeautifulSoup

from instalooter.batch import BatchRunner

from instagrabber.models import InstaConfig, InstaPicture, InstaUser
import StringIO
import shutil

class Command(BaseCommand):


    def handle(self, *args, **options):
        config = InstaConfig.objects.first()
        tmp_dir = "/tmp/instagram"
        

        looter_cfg = StringIO.StringIO()
        looter_cfg.write("[INSTAGRABBER]\n")
        # looter_cfg.write("username = %s\n" % settings.INSTAGRAM_LOGIN)
        # looter_cfg.write("password = %s\n" % settings.INSTAGRAM_PWD)
        looter_cfg.write("dump-only = true\n")
        looter_cfg.write("extended-dump = true\n")  
        looter_cfg.write("quiet = true\n")  
        looter_cfg.write("users =\n")
        looter_cfg.write("\tmario.mousse: %s\n" % tmp_dir)
        looter_cfg.write("hashtag =\n")
        looter_cfg.write("\tmariomousse: %s\n" % tmp_dir)
        looter_cfg.seek(0)
        batch_runner = BatchRunner(looter_cfg)
        batch_runner.run_all()

        images = []
        for root, dirnames, filenames in os.walk(tmp_dir):
            for filename in fnmatch.filter(filenames, '*.json'):
                with open(os.path.join(root, filename)) as json_file: 
                    images.append(json.load(json_file))
        
        new_pictures = 0
        for img in images:
            if img["__typename"] == "GraphImage":
                params = {
                    "instagram_id" : img["id"],
                    "instagram_url" : img["thumbnail_src"],
                    "datetime" : datetime.utcfromtimestamp(img["taken_at_timestamp"]),
                }
                
                try :
                    params["caption"] = img["edge_media_to_caption"]["edges"][0]["node"]["text"]
                except Exception as e:
                    pass

                try:
                    params["user"] = InstaUser.objects.get(user_id=img["owner"]["id"])
                except InstaUser.DoesNotExist:
                    ## FROM https://stackoverflow.com/a/53680672
                    r = requests.get('https://www.instagram.com/p/%s/' % img["shortcode"])
                    soup = BeautifulSoup(r.content, "lxml")
                    scripts = soup.find_all('script', type="text/javascript", text=re.compile('window._sharedData'))
                    stringified_json = scripts[0].get_text().replace('window._sharedData = ', '')[:-1]
                    params["user"] = InstaUser.objects.create(
                        user_id=img["owner"]["id"],
                        username=json.loads(stringified_json)['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['username'])
                    
                if params["user"].username in config.backlist.replace(' ','').split(','):
                    params["user"].delete()
                else:
                    if not InstaPicture.objects.filter(instagram_id=img["id"]).exists():
                        InstaPicture.objects.create(**params)
                        new_pictures += 1
                    
                    pic = InstaPicture.objects.get(instagram_id=img["id"])
                    
                    try:
                        pic.likes = img["edge_liked_by"]["count"]
                        pic.save()
                    except Exception as e:
                        pass

        for root, dirnames, filenames in os.walk(tmp_dir):
            for filename in fnmatch.filter(filenames, '*.json'):
                os.remove(os.path.join(root, filename))
        
        if config.notif_email and new_pictures > 0:
            from django.core.mail import send_mail
            from django.contrib.sites.models import Site
            
            send_mail(
                '%s Social Wall' % Site.objects.get(pk=1).name,
                '%s post(s) sont soumis à modération' % new_pictures,
                settings.DEFAULT_FROM_EMAIL,
                [config.notif_email],
                fail_silently=True,
            )
