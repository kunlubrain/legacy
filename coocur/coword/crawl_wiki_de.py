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

CRAWLED_LINKS = {}

def crawl_getSoup(seed):

    url = 'https://de.wikipedia.org/wiki/' + seed

    try:
        return kutils.get_soup_retry(url, minsleep=1, maxretry=3, logging=1)
    except:
        print "ERR: bad seed:", url
        return None

# find all links that can be crawled further
def crawl_getSeedableLinks(soup):
    try:
        term = soup.find('h1', id='firstHeading').text
    except:
        return 1, "NO H1 FOUND !!!"

    try:
        body = soup.find('div', id='bodyContent')
        links = body.find_all('a', href=re.compile("^/wiki/[A-Z][a-z_\(\)]+$"))

        seeds = set([l.get('href') for l in links])
        seeds = [re.sub(r'^/wiki/', '', s) for s in seeds]

    except:
        return 1, "NO SEED FOUND !!!"

    return 0, seeds

def crawl_getText(soup):
    text = ''
    try:
        paras = soup.find_all('p')
        for p in paras:
            prev = p.findPreviousSibling(name=re.compile('^h.*'))
            if prev: prev = prev.text
            else: prev = "NIL"

            ignoreRegex='^(Note|Reference|See also)'
            if re.search(ignoreRegex, prev):
                continue

            text += p.text
    except:
        return 1, "ERR: no p-tag found !!!"

    return 0, text

def crawl_seed(seed, verbose=None):
    soup = crawl_getSoup(seed)

    errcode, seeds = crawl_getSeedableLinks(soup)
    if errcode:
        print "Bad seed:", seed
        print seeds
        raise Exception

    if verbose:
        for s in seeds: print s

    errcode, text = crawl_getText(soup)
    if errcode:
        print "Bad seed:", seed
        print text
        raise Exception

    saveText2File(seed, text)
    if verbose:
        print "Crawled:", seed, "Saved under data_wiki_de"

    return seeds

def saveText2File(seed, text):
    filename = 'data_wiki_de/'+seed
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(text)

CRAWLED_SEEDS = {}

def crawlFrom(seed):

    remainingSeeds = [seed]

    while remainingSeeds:
        newseeds = []
        for s in remainingSeeds:
            seeds = crawl_seed(s)
            CRAWLED_SEEDS[seed] = 1

            newseeds += [s for s in seeds if not s in CRAWLED_SEEDS and not s in remainingSeeds]
        remainingSeeds = set(newseeds)

crawlFrom('Text_Mining')
