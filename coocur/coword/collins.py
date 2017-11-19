# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS
import kutils
import urllib2
from urlparse import urljoin
import re

DICT = {}
SEEDS = {}

def readin():
    with open('collins.txt', 'r') as f:
        for line in f:
            word = line.split(':', 1)[0]
            DICT[word] = 1
    with open('collins_part2.txt', 'r') as f:
        for line in f:
            word = line.split(':', 1)[0]
            DICT[word] = 1
    with open('dictWordTypes.txt') as f:
        for line in f:
            word = line.split(':', 1)[0]
            if not word in DICT:
                SEEDS[word] = 1

readin()
print "existing dict size=", len(DICT)
print "existing seed size=", len(SEEDS)

def _stop(): raw_input('...')

def __goodText(text):
    wordList = text.split()
    words = [w.lower() for w in wordList if re.match('^\w+$', w)]
    words = [w for w in words if not w in DICT]
    words = [w for w in words if not re.search('\d+', w)]
    return words

def crawl(seed):
    baselink = 'http://www.collinsdictionary.com/dictionary/english/'
    url = baselink + seed

    __FRONTIER = []

    try:
        soup = kutils.get_soup_retry(url, minsleep=1, maxretry=5)
    except:
        print "!!! BAD SOUP for ", url
        return []

    # find word
    rec = soup.find_all(attrs={'class':'orth h1_entry'})
    if len(rec)<1:
        print "!!! NO REC!"

    for r in rec:

        #this does not work for word 'approve' due to different layout
        #word = r.find('span').previousSibling

        # this works:
        try:
          children = r.findChildren()
          if len(children)>0:
              firstChild = children[0]
              word = firstChild.previousSibling
          else:
              word = r.text
        except:
            print "bad formed word rec:", r
            for c in r.findChildren():
                print "child:", c
            raise Exception
            continue

        if not word:
            print "!!!BAD: no word found:", word
            with open('collinsbad.rec', 'a') as f:
                try:
                    line = seed+':%s'%r
                except:
                    line = seed
                f.write(re.sub('\n','',line))
            continue

        print "found::", word
        if not re.match('^[a-z]+$', word): continue

        #print "find pos"
        div = r.find_next('div', attrs={'class':'definitions hom-subsec'})
        pos =[s.text for s in div.find_all('span', attrs={'class':'pos'})]
        postext = ';'.join(pos)

        #print "TEXT OF POS-DIV", div.text

        print "guess good word in", div.text
        __FRONTIER += __goodText(div.text)

        save(seed + ':' + word + ':' + postext)

    __FRONTIER = list(set(__FRONTIER))
    raw_input('---done---, url='+url+' newfrontiersize=%s; '%len(__FRONTIER)+','.join(__FRONTIER))
    return __FRONTIER

def save(line):
    print "save it:", line
    with open('collins.txt', 'a') as f:
        f.write(line+'\n')

if 0:
    #crawl('xy')
    crawl('perked')
    #crawl('m')
    raw_input()

def crunch():
    seed = 'release'
    seed = 'improve'
    seed = 'generate'
    seed = 'coerce'
    seed = 'optimize'
    seed = 'abstract'
    seed = 'intermediate'
    seed = 'bound'
    seed = 'crawl'
    seed = 'brain'
    seed = 'synapse'
    seed = 'lobe'
    seed = 'approve'
    for seed in SEEDS:
      DICT[seed] = 1
      frontier = crawl(seed)
      while(frontier):
          print "process frontier, size=", len(frontier)
          with open('collinsFrontier.txt', 'w') as f: f.write('FRO:'+','.join(frontier))
          # put this here before iterating the urls
          for w in frontier: DICT[w] = 1

          newfrontier = []
          for w in frontier:
              newfrontier += crawl(w)
              with open('collinsFrontier.txt', 'w') as f: f.write('NEW:'+','.join(newfrontier))
          newfrontier = list(set(newfrontier))
          frontier = newfrontier
          print('---new frontier size=%s, dictsize=%s'%(len(frontier), len(DICT)))
      #raw_input()
crunch()
raw_input('---ALL CRUNCH DONE---')

# SEEDS = [approve, coming, learning, computing, result, compete, completely, importantly, reveal,suggest, containing, contains]


# some words in 'dic.txt' are not indexed by 'collins'
# some, like asian -> Asian, are mis-formed
# some, like pyramical in 'collins' are derivative form ---> crawk for those too
