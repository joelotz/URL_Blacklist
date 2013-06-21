# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 17:31:16 2013

@author: joe
"""

import Blacklist as bl


def scrape_url(url):
    
    dirtyList     = bl.scrape_site(url)
    cleanList     = bl.clean_list(dirtyList)
    sanitizedList = bl.sanitize_list(cleanList)
#    bl.upload2db(sanitizedList,url)    
    
    print dirtyList
    print cleanList
    print sanitizedList    
    print "completed"
    return

def import_url_file(fileName):
    fileList  = bl.open_file(fileName)
    cleanList = bl.clean_list(fileList)
    sanitizedList = bl.sanitize_list(cleanList)
    bl.upload2db(sanitizedList)
    return


#fileName = 'urlList.txt'
#s = import_url_file(fileName)

url = 'www.hottystop.com'
scrape_url(url)    
