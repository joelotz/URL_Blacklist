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
from urlparse import urlparse

def scrape_site(url):
    dirtyList = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text,"html.parser",parse_only=SoupStrainer("a"))
    for link in soup:
        temp = urlparse(link.get('href'))
        dirtyList.append(temp.netloc)
    return dirtyList
    
def clean_list(dirtyList):
    cleanList = filter(None, dirtyList)  # remove blanks
    cleanList = list(set(dirtyList))     # remove duplicates
    return cleanList

def sanitize_list(cleanList,whitelistName="whitelist.csv"):
    f = open(whitelistName)
    whiteList = [line.strip() for line in f]
    f.close()
    whiteList = clean_list(whiteList)
    sanitizedList = set(cleanList) - set(whiteList)#filter(None, dirtyList)
    return sanitizedList    

def upload_db():
    return
    
###################################    
url = "http://www.xvideos.com"

dirtyList = scrape_site(url)
cleanList = clean_list(dirtyList)
sanitizedList = sanitize_list(cleanList)


    
    