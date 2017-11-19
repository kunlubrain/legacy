# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS
import re
import kutils
from urlparse import urljoin
import codecs
import os
import time
import urllib2
import codecs
import os
import time

Records = {}
FileLinkRecords = 'wikiRecTmp.txt'
FileLinkRecords = 'wikiRec.txt'
FileLinkRecords = 'wikiRecCut.txt'

def crawl(seed):
    baselink = 'https://en.wikipedia.org/wiki/'
    url = baselink + seed
    url = 'http://www.wsj.com/news/technology'
    url = 'http://blogs.wsj.com/digits/2015/12/18/quiz-test-your-2015-tech-news-iq/?mod=ST1'

    try:
        soup = kutils.get_soup_retry(url, minsleep=3, maxretry=5)
    except:
        _registerBad("NO SOUP FOUND FOR ::" + seed)

    try:
        content = soup.find('div', {'class':'post-content'})
        paras = content.find_all('p')
        text = ''
        for p in paras: text += p.text
        print ">\n", text
    except:
        print "Bad content"

    try:
        links = soup.find_all('a', href=re.compile(".*blogs.*digits"))

        seeds = set([l.get('href') for l in links])
        seeds = [s for s in seeds if not s in Records]

        Records[seed] = 1

    except:
        print Exception
        return []

    for s in seeds: print s

    return seeds

crawl("foo")
raw_input()

def crawlWikiText(seed):
    baselink = 'https://en.wikipedia.org/wiki/'
    url = baselink + seed

    try:
        soup = kutils.get_soup_retry(url, minsleep=1, maxretry=3, logging=False)
    except:
        print "ERR: bad seed:", url
        return ''

    text = ''
    try:
    #if 1:
        paras = soup.find_all('p')
        for p in paras:
            prev = p.findPreviousSibling(name=re.compile('^h.*'))
            if prev: prev = prev.text
            else: prev = "NIL"
            ignoreRegex='^(Note|Reference|See also)'
            if re.search(ignoreRegex, prev):
                continue
            #print "\n\n####################################, prev=", prev
            #print p.text
            text += p.text
    except:
        print "ERR: no p-tag found for", url
        return ''

    return text

def crunch():
    seeds = crawl('Text_mining')
    while(seeds and len(Records)<10):
        print("process seeds, #=%s"%len(seeds))
        for s in seeds: Records[s]=1
        newseeds = []
        for seed in seeds:
            newseeds += crawl(seed)
        seeds = set(newseeds)

crunch()
print "all done"
for r in Records:
     print r
