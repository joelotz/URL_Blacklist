# -*- coding: utf-8 -*-
'''
-------------------------------------------------------------------------------
Filename   : blacklist_scraper.py
Date       : 2013-2-25
Author     : Joe Lotz <joelotz@gmail.com>
-------------------------------------------------------------------------------
'''
import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

def scrape_site():
    return
    
def clean_links():
    return
    
def upload_db():
    return
    
url = "http://www.xvideos.com"
r = requests.get(url)
soup = BeautifulSoup(r.text,"html.parser",parse_only=SoupStrainer("a"))
for link in soup:
    print(link.get('href'))
    
    