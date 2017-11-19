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

def _registerBad(s):
    print s
    with open('wikiBad.txt', 'a') as f: f.write(s+'\n')

def __save(term, seed, links):
    with open(FileLinkRecords, 'a') as f:
        f.write("%s::%s::%s\n"%(term, seed, ':::'.join(links)))

def __getSeeds():
    seeds = {}
    print "get seeds from", FileLinkRecords
    with open(FileLinkRecords, 'r') as f:
        for line in f:
            seed = line.split('::',2)[1]
            links = line.split('::',2)[-1].split(':::')
            seeds[seed]=1
            for link in links: seeds[link]=seeds.get(link,0)+1
    n=0
    for i in seeds: n+=seeds[i]
    print "total seeds", len(seeds), " raw total", n
    return seeds

def crawl(seed):
    baselink = 'https://en.wikipedia.org/wiki/'
    url = baselink + seed

    try:
        soup = kutils.get_soup_retry(url, minsleep=3, maxretry=5)
    except:
        _registerBad("NO SOUP FOUND FOR ::" + seed)

    try:
        term = soup.find('h1', id='firstHeading').text
    except:
        _registerBad("NO H1 FOUND FOR" + seed)
        return []

    try:
        body = soup.find('div', id='bodyContent')
        links = body.find_all('a', href=re.compile("^/wiki/.*"))
        links = body.find_all('a', href=re.compile("^/wiki/[A-Z][a-z_\(\)]+$"))

        seeds = set([l.get('href') for l in links])
        seeds = [s for s in seeds if not s in Records]
        seeds = [re.sub(r'^/wiki/', '', s) for s in seeds]

        Records[seed] = (term, seeds)
        __save(term, seed, seeds)

        print "new seeds #=", len(seeds)

        if 0:
            for s in seeds: print s
            for l in links: print l.text
    except:
        _registerBad("NO SEED FOUND FOR ::" + seed)
        return []

    return seeds

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
    while(seeds):
        print("process seeds, #=%s"%len(seeds))
        for s in seeds: Records[s]=1
        newseeds = []
        for seed in seeds:
            newseeds += crawl(seed)
        seeds = set(newseeds)

def tokenize(text):
    words = re.findall('\w+', text)
    return words

def tokenset(text):
    def __normalize(mo): return mo.group(0).lower()
    text = re.sub(r'\b[A-Z][a-z]', __normalize, text)
    words = set(re.findall('\w+', text))                        # <--- !!! Wonderful
    return [w for w in words if not re.search(r'\d', w)]

def cruchWikiText():

    seeds = __getSeeds()
    seeds = [s for s in seeds if not s in SEEDS_DOWNLOADED]


    total = len(seeds)
    patch_num = 0
    print "save wiki text for %s pages"%(total)

    for seed in seeds:

      text     = crawlWikiText(seed)
      words    = tokenset(text)
      filename = 'data_wiki_de/'+seed
      with codecs.open(filename, 'w', 'utf-8') as f:
        data = "%s\n%s"%(seed, text)
        f.write(data)


# do this before downloading further seeds
def findAllSeedsDownloaded():
    ff = os.listdir('data')
    print "Exist %s seeds (text already downloaded)"%len(ff)
    return ff

SEEDS_DOWNLOADED = findAllSeedsDownloaded()
