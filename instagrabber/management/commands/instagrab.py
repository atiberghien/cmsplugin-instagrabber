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
from instagram_scraper.app import InstagramScraper

from instagrabber.models import InstaConfig, InstaPicture, InstaUser


class Command(BaseCommand):


    
    def handle(self, *args, **options):
        config = InstaConfig.objects.first()

        search_terms = set(config.search_accounts.split(',') + config.search_hashtags.split(','))

        params = {
            'login_user': settings.INSTAGRAM_LOGIN, 
            'login_pass': settings.INSTAGRAM_PWD,  
            'usernames': search_terms,  
            'destination': '/tmp/instagram/usernames',
            'media_types': ['none'], 
            'include_location': True, 
            'media_metadata': True, 
            'tag': False, 
            "quiet" : True,
        }
        scraper = InstagramScraper(**params)
        scraper.authenticate_with_login()
        scraper.scrape()
        scraper.save_cookies()

        params.update({
            'usernames': search_terms,
            'destination': '/tmp/instagram/tags',
            'tag': True, 
        })
        scraper = InstagramScraper(**params)
        scraper.authenticate_with_login()
        scraper.scrape_hashtag()
        scraper.save_cookies()

        images = []
        for root, dirnames, filenames in os.walk('/tmp/instagram'):
            for filename in fnmatch.filter(filenames, '*.json'):
                with open(os.path.join(root, filename)) as json_file: 
                    data = json.load(json_file)
                    if not images:
                        images = data["GraphImages"]
                    else:
                        images.extend(data["GraphImages"])
        
        new_pictures = 0
        for img in images:

            params = {
                "instagram_id" : img["id"],
                "instagram_url" : img["thumbnail_src"],
                "datetime" : datetime.utcfromtimestamp(img["taken_at_timestamp"]),
            }
            
            try :
                params["caption"] = img["edge_media_to_caption"]["edges"][0]["node"]["text"]
            except Exception, e:
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
                    
                if 'tags' in img and img["tags"]:
                    pic.tags.add(*img["tags"])
                
                try:
                    pic.likes = img["edge_media_preview_like"]["count"]
                    pic.save()
                except Exception, e:
                    print('https://www.instagram.com/p/%s/' % img["shortcode"])

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
