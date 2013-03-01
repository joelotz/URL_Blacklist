# -*- coding: utf-8 -*-
'''
-------------------------------------------------------------------------------
Filename   : Blacklist.py
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
_TABLE = "blacklist_test"

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

def sanitize_list(cleanList,whiteListName="whitelist.csv"):
    try:    
        # Open the whitelist     
        whiteList = open_file(whiteListName)
        whiteList = clean_list(whiteList)
        sanitizedList = set(cleanList) - set(whiteList)#filter(None, dirtyList)
    except:
        sanitizedList = cleanList
        print "Error: "
    return sanitizedList    

def open_file(fileName):
    try:
        # Open the whitelist     
        f = open(fileName)
        fileList = [line.strip() for line in f]
        fileList = [x.lower() for x in fileList]
        f.close()
    except:
        if f:
            f.close()
        print "Error: Unable to open file."            
    return fileList
    

def upload2db(urlList,url=''):
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

def scrape_url(url):
    dirtyList     = scrape_site(url)
    dirtyList     = prefix_url(dirtyList)    
    cleanList     = clean_list(dirtyList)
    sanitizedList = sanitize_list(cleanList)
    upload2db(sanitizedList,url)
    return

def import_url_file(fileName):
    fileList      = open_file(fileName)
    fileList      = prefix_url(fileList)        
    cleanList     = clean_list(fileList)
    sanitizedList = sanitize_list(cleanList)
    prefixList    = prefix_url(sanitizedList)
    upload2db(prefixList)
    return

def read_from_db(num=20):
    try:
        # Open database connection
        conn = MySQLdb.connect(host = _HOST, 
                             user = _USER, 
                             passwd = _PASS,
                             db = _DATA)
        
        # prepare a cursor object using cursor() method
        cursor = conn.cursor()
        sql = "SELECT url FROM %s WHERE referrer='' ORDER BY date_entered DESC LIMIT %d;"
        cursor.execute(sql % (_TABLE,num))
        selectList = []
        for row in cursor.fetchall() :
            selectList.append(row[0])
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:    
        if conn:    
            conn.close()  # disconnect from server
            cursor.close() # close cursor object
    return selectList
    
def prefix_url(urlList):
    prefixList = []
    for link in urlList:
        if link.startswith( 'http://' ):
            prefixList.append(link)
        elif link.startswith( 'www' ):
            link = "http://" + link
            prefixList.append(link)
        elif link.startswith( 'enter.'):    
            link = "http://" + link[6:]
        elif link.startswith( 'blog.'):    
            link = "http://" + link[5:]
        elif link.startswith( 'join.'):    
            link = "http://" + link[5:]
        elif link.startswith( 'm.'):    
            link = "http://" + link[2:]
        elif link.startswith( 'stats.'):    
            link = "http://" + link[6:]
        elif link.startswith( 'static.'):    
            link = "http://" + link[7:]            
        else:
            link = "http://www."+ link
            prefixList.append(link)
    return prefixList
    

#fileName = 'urlList.txt'
#s = import_url_file(fileName)

#url = "http://www.xvideos.com"
#scrape_url(url)    

selectList = read_from_db(num=40)
for link in selectList:
    scrape_url(link)
    print "Completed"    
    