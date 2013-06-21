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
_DATE  = time.strftime('%Y-%m-%d')


#__!!! This will be pulled out, just credentials for local db
##------------------------------##
##  My MySQL Login Info  ##
_HOST  = "localhost"
_USER  = "blacklist_admin"
_PASS  = "charlie1"
_DATA  = "blacklist"
_TABLE = "blacklist"
##------------------------------##



def scrape_site(url):
    """ 
    This function scrapes the supplied website and produces a list of website
    links on the webpage.    
    
    Input:  'url' = website to be scraped
    Output: 'dirtyList' = list of links from website, not cleaned in anyway 
            so it contains blanks and non-formatted links.
    
    Dependencies: BeautifulSoup, urlparse, requests   
    """
    try:
        if not url.startswith("http://"): url = "http://"+url
        r = requests.get(url)  # pull content of url

        soup = BeautifulSoup(r.text,"html.parser",parse_only=SoupStrainer("a"))
        #dirtyList = [(urlparse(url)).netloc] # add url to the list 
        dirtyList = [url]
        
        # loop through soup and pull out each href link
        for link in soup: 
            temp = urlparse(link.get('href'))
            dirtyList.append(temp.netloc)
        
        # if scraped site is not new, update date checked scraped
        # the idea is to use this metadata to decide priority "score"
        update_date_checked(url) 
        
        # format everything in lowercase
        dirtyList = [x.lower() for x in dirtyList]
    except:  
    # if something is broken deactivate site so we don't waste time in the future    
        inactivate_site(url)
        #print ("Site '%s' is inactive" % url)
        print ("Site is inactive")        
    return dirtyList

def prefix_url(urlList):
    """
    Takes a list of urls and formats them consistently.
    http://www.website.com
    
    Inputs:  'urlList' = list of unformatted prefixes
    Outputs: 'prefixList' = formatted urlList
    """
    prefixList = []
    for link in urlList:
        if link.startswith( 'http://' ):
            prefixList.append(link)
        elif link.startswith( 'www' ):
            link = "http://" + link
            prefixList.append(link)
        elif link.startswith( 'enter.'):
            link = "http://" + link[6:]
            prefixList.append(link)
        elif link.startswith( 'blog.'):
            link = "http://" + link[5:]
            prefixList.append(link)
        elif link.startswith( 'join.'):
            link = "http://" + link[5:]
            prefixList.append(link)
        elif link.startswith( 'm.'):
            link = "http://" + link[2:]
            prefixList.append(link)
        elif link.startswith( 'stats.'):
            link = "http://" + link[6:]
            prefixList.append(link)
        elif link.startswith( 'static.'):
            link = "http://" + link[7:]
            prefixList.append(link)
        elif link.startswith( 'tour.'):
            link = "http://" + link[5:]
            prefixList.append(link)
        elif link.startswith( 'access.'):
            link = "http://" + link[7:]
            prefixList.append(link)
        elif link.startswith( 'members.'):
            link = "http://" + link[8:]
            prefixList.append(link)
        elif link.startswith(''):
            continue
        else:
            link = "http://www."+ link
            prefixList.append(link)
    return prefixList


def clean_list(dirtyList):
    """ 
    Takes a list and removes blanks and duplicates.
    
    Inputs:  'dirtyList' = list of urls
    Outputs: 'cleanList' = no blanks or duplicates
    """    
    cleanList = filter(None, dirtyList)  # remove blanks
    cleanList = list(set(dirtyList))     # remove duplicates
    return [x.lower() for x in cleanList]


def sanitize_list(cleanList,whiteListName="whitelist.csv"):
    """
    Removes whitelisted items from a list
    
    Inputs:  'cleanList' = list of urls
              'whiteListName' = name of whitelist
    Outputs: 'sanitizedList' = cleanList without items from whitelist
    """
    whiteList = open_file(whiteListName)
    whiteList = clean_list(whiteList)
    sanitizedList = list(set(cleanList) - set(whiteList))
    return sanitizedList

def upload2db(urlList,url=''):
    """
    Uploads list of urls to the database
    
    Inputs:  'urlList' = list of urls to upload to db
             'url' = url of referring site, used to give credit for num of links
    Outputs: 'cnt' = the number of links uploaded to the db, used for scoring
    """
    cnt = 0 # intialize counter
    conn, cursor = connect2db() # connect to database
    
    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO %s (url, active, date_entered, source) \
           VALUES ('%s', '%d', '%s', '%s');"
    
    for link in urlList:
        try:
            cursor.execute(sql % (_TABLE, link, 1, _DATE, _USER))
            cnt = cnt + 1
        except:
            cnt = cnt
    conn.commit()
    conn.close()  # disconnect from server
    cursor.close() # close cursor object
    print ("Site gave %d links" % cnt)
    
    # Give credit to referring site for num of links    
    if (cnt>0 and url!=''): 
        link = [(urlparse(url)).netloc]
        link = prefix_url(link)
        update_num_links(cnt, link[0])
    return cnt    

def update_num_links(cnt,url):
    """ 
    Updates a url with the number of links last scraped
    
    Inputs:  'cnt' = number of links
             'url' = url to give credit to
    Outputs: None
    
    <called from upload2db>
    """  
    try:
        conn, cursor = connect2db()
        sql = "SELECT links FROM %s WHERE url='%s';"
        cursor.execute(sql % (_TABLE, url))
        for row in cursor.fetchall(): old_links = row[0]
        if old_links==-1: old_links=0  # set to 0 so we know that it has been looked at
        sql = "UPDATE %s SET links=%d WHERE url='%s';"
        cursor.execute(sql % (_TABLE, cnt+old_links, url))
        conn.commit()
    except:
        print "Error: while updating links"
    finally:
        conn.close()  # disconnect from server
        cursor.close() # close cursor object
    return

#######################################################################
##  HELPER FUNCTIONS  
#######################################################################

def update_date_checked(url):
    """
    Update existing url with the latest date checked.
    
    Input:  'url' = existing website that was re-scraped
    <Gets called from scrape_site>
    """
    try:
        conn, cursor = connect2db()
        sql = "UPDATE %s SET date_checked='%s' WHERE url='%s';"
        cursor.execute(sql % (_TABLE,_DATE,url))
        conn.commit()
    except:
        print "Error: while inactivating url"
    finally:
        conn.close()  # disconnect from server
        cursor.close() # close cursor object
    return

def inactivate_site(url):
    """
    Deactivating an existing url.
    
    Input:  'url' = existing website that should be inactive.
    <Gets called from scrape_site>    
    """
    try:
        conn, cursor = connect2db()
        sql = "UPDATE %s SET active=0 WHERE url='%s';"
        cursor.execute(sql % (_TABLE,url))
        conn.commit()
    except:
        print "Error: while inactivating url"
    finally:
        conn.close()  # disconnect from server
        cursor.close() # close cursor object
    return

def open_file(fileName):
    try:
        fileList = []
        # Open the whitelist
        f = open(fileName)
        fileList = [line.strip() for line in f]
        fileList = [x.lower() for x in fileList]
    except IOError:
        print "Error: Unable to open file."
    finally:
        f.close()
    return fileList

def connect2db():
    try:
        # Open database connection
        conn = MySQLdb.connect(host=_HOST, user=_USER, passwd=_PASS, db=_DATA)
        # prepare a cursor object using cursor() method
        cursor = conn.cursor()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    return conn,cursor

#######################################################################
##   UTILTY FUNCTIONS
#######################################################################


def read_from_db(num=10,links=0,readType=0):
    """
    Pulls all links from database
    """
    try:
        conn, cursor = connect2db()
        if readType==0:
            sql = "SELECT url FROM %s WHERE active=1 AND links<%d ORDER BY date_entered DESC LIMIT %d;"            
        else:
            sql = "SELECT url FROM %s WHERE active=1 AND links>%d ORDER BY links DESC LIMIT %d;"                
        cursor.execute(sql % (_TABLE,links,num))
        selectList = []
        for row in cursor.fetchall(): selectList.append(row[0])
    except:
        print "Error: Reading from database"
    return selectList

def clean_db(whiteListName="whitelist.csv",isListFile=1):
    """
    Removes whitelist items from the database
    """
    
    if isListFile==1: 
        whiteList = open_file(whiteListName)
    else:
        whiteList = whiteListName
    conn, cursor = connect2db()
    sql = "DELETE FROM %s WHERE url='%s';"
    for link in whiteList:
        try:
            cursor.execute(sql % (_TABLE, link))
        except:
            print "Error: Writing to database"
    conn.commit()            
    conn.close()  # disconnect from server
    cursor.close() # close cursor object
    return

def import_url_file(fileName):
    fileList  = open_file(fileName)
    cleanList = clean_list(fileList)
    sanitizedList = sanitize_list(cleanList)
    upload2db(sanitizedList)
    return
    
"""
def scrape_url(url):
    dirtyList     = scrape_site(url)
    cnt = clean_and_upload(dirtyList,url)
    return cnt

def import_url_file(fileName):
    dirtyList      = open_file(fileName)
    clean_and_upload(dirtyList)
    return

def run(num=20):
    selectList = read_from_db(num=30,links=0,readType=0)
    for link in selectList:
        scrape_url(link)
    print "Completed"
    return
"""
"""
def clean_and_upload(dirtyList,url):
    dirtyList     = prefix_url(dirtyList)
    cleanList     = clean_list(dirtyList)
    sanitizedList = sanitize_list(cleanList)
#    cnt = upload2db(sanitizedList,url)
    return cnt
"""

#######################################################################
#  BREAKDOWN FOR DEVELOPMENT
#######################################################################

url = 'http://www.bodsforthemods.com'  # starting url
dirtyList     = scrape_site(url)
prefixList    = prefix_url(dirtyList)
cleanList     = clean_list(prefixList)
sanitizedList = sanitize_list(cleanList)
cnt           = upload2db(sanitizedList,url)
