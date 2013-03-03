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


def scrape_site(url,new):
    dirtyList = []
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text,"html.parser",parse_only=SoupStrainer("a"))
        for link in soup:
            temp = urlparse(link.get('href'))
            dirtyList.append(temp.netloc)
        dirtyList = [x.lower() for x in dirtyList]
        update_date_checked(url) # if scraped site is not new, update date checked
    except:
        inactivate_site(url)
    return dirtyList

def update_date_checked(url):
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

def clean_list(dirtyList):
    cleanList = filter(None, dirtyList)  # remove blanks
    cleanList = list(set(dirtyList))     # remove duplicates
    return [x.lower() for x in cleanList]

def sanitize_list(cleanList,whiteListName="whitelist.csv"):
    whiteList = open_file(whiteListName)
    whiteList = clean_list(whiteList)
    sanitizedList = list(set(cleanList) - set(whiteList))
    return sanitizedList

def open_file(fileName):
    try:
        # Open the whitelist
        f = open(fileName)
    except IOError:
        print "Error: Unable to open file."
    finally:
        fileList = [line.strip() for line in f]
        fileList = [x.lower() for x in fileList]
        f.close()
    return fileList

def connect2db():
    try:
        # Open database connection
        conn = MySQLdb.connect(host= _HOST, user= _USER, passwd= _PASS, db= _DATA)
        # prepare a cursor object using cursor() method
        cursor = conn.cursor()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    return conn,cursor

def upload2db(urlList,url=''):
    cnt = 0 # intialize counter
    # connect to database
    conn, cursor = connect2db()
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
    print "Number of rows affected: %d" % cnt
    if (cnt>0 and url!=''): update_num_links(cnt,url)

    return

def update_num_links(cnt,url):
    try:
        conn, cursor = connect2db()
        sql = "SELECT links FROM %s WHERE url='%s';"
        cursor.execute(sql % (_TABLE, url))
        for row in cursor.fetchall(): old_links = row[0]

        sql = "UPDATE %s SET links=%d WHERE url='%s';"
        cursor.execute(sql % (_TABLE, cnt+old_links, url))
        conn.commit()
    except:
        print "Error: while udating links"
    finally:
        conn.close()  # disconnect from server
        cursor.close() # close cursor object
    return

def read_from_db(num=20,links=1):
    try:
        conn, cursor = connect2db()
        sql = "SELECT url FROM %s WHERE active=1 AND links<%d ORDER BY date_entered DESC LIMIT %d;"
        cursor.execute(sql % (_TABLE,links,num))
        selectList = []
        for row in cursor.fetchall(): selectList.append(row[0])
    except:
        print "Error: Reading from database"
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
        elif link.startswith( 'members.'):
            link = "http://" + link[7:]
            prefixList.append(link)
        elif link.startswith( ' '):
            continue
        else:
            link = "http://www."+ link
            prefixList.append(link)
    return prefixList

def scrape_url(url,new):
    dirtyList     = scrape_site(url,new)
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

##fileName = 'urlList.txt'
#s = import_url_file(fileName)

selectList = read_from_db(num=10)
for link in selectList:
    scrape_url(link,new=0)
print "Completed"

