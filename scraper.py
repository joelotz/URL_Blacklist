# -*- coding: utf-8 -*-
'''
-------------------------------------------------------------------------------
Filename   : scraper.py
Date       : 2013-2-25
Author     : Joe Lotz <joelotz@gmail.com>
-------------------------------------------------------------------------------
'''
##------------------------------##
import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from urlparse import urlparse
import MySQLdb
import sys
import time


##------------------------------##

##  My MySQL Login Info  ##
_HOST  = "localhost"
_USER  = "blacklist_admin"
_PASS  = "charlie1"
_DATA  = "blacklist"
_TABLE = "blacklist"

_DATE  = time.strftime('%Y-%m-%d')
##------------------------------##


def scrape_site(url):
    dirtyList = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text,"html.parser",parse_only=SoupStrainer("a"))
    for link in soup:
        temp = urlparse(link.get('href'))
        dirtyList.append(temp.netloc)
    return [x.lower() for x in dirtyList]
    
def clean_list(dirtyList):
    cleanList = filter(None, dirtyList)  # remove blanks
    cleanList = list(set(dirtyList))     # remove duplicates
    return [x.lower() for x in cleanList]

def sanitize_list(cleanList,whitelistName="whitelist.csv"):
    try:    
        # Open the whitelist     
        f = open(whitelistName)
        whiteList = [line.strip() for line in f]
        whiteList = [x.lower() for x in whiteList]
        f.close()
        whiteList = clean_list(whiteList)
        sanitizedList = set(cleanList) - set(whiteList)#filter(None, dirtyList)
    except:
        sanitizedList = cleanList
        print "Error: "
    return sanitizedList    
    

def upload2db(urlList):
    try:
        # Open database connection
        conn = MySQLdb.connect(host = _HOST, 
                             user = _USER, 
                             passwd = _PASS,
                             db = _DATA)
        
        # prepare a cursor object using cursor() method
        cursor = conn.cursor()
        # Prepare SQL query to INSERT a record into the database.
        sql = "INSERT INTO %s(url, active, date_entered, data_source, \
            referrer, links) VALUES ('%s', '%d', '%s', '%s', '%s', '%d');"
        
        cnt = 0                
        # Execute the SQL command5
        for link in urlList:
            try:
                cursor.execute(sql % (_TABLE, link, 1, _DATE, _USER, url, 0))
                cnt = cnt + 1
            except:
                cnt = cnt
                
        ###***** Maybe update url with links=cnt                
        # Commit your changes in the database
        conn.commit()
        print "Number of rows affected: %d" % cnt
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:    
        if conn:    
            conn.close()  # disconnect from server
            cursor.close() # close cursor object
    return
    
###################################
###################################

url = "google.com"

dirtyList     = scrape_site(url)
cleanList     = clean_list(dirtyList)
sanitizedList = sanitize_list(cleanList)
status        = upload2db(sanitizedList)

print "completed"
    
    