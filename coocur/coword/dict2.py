# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS
import re
import kutils
from urlparse import urljoin
import codecs
import os
import time
import urllib2

def trim(s): return s.replace('\n','').replace('\t','').replace('\r','')

#<ul class="dict-basic-ul">
#  <li><span>vt.</span><strong>开车；驱赶；迫使
#  <li><span>n.</span><strong>驾车；驱使；推进力；路 ... [计]驱动器
#  <li style="padding-top: 25px;">

#<div class="basic clearfix">
#<ul>
#<li><span>int.</span><strong>[表示不耐烦或恼怒]嗨</strong></li>


# <div class="shape" style="clear:both;">
# <span>
# <label>名词:</label>
# <a href="http://dict.cn/suggester" target="_blank">suggester</a>
# <span>
# <label>过去式:</label>
# <a href="http://dict.cn/suggested" target="_blank">suggested</a>

__VOCAB__ = {}

def crawl(w):
  url="http://dict.cn/%s"%w
  try:
    soup = kutils.get_soup_retry(url, minsleep=0, maxretry=0)
  except:
    with open('pos_dict_badurl.txt', mode='a') as f:
        print "bad url", w
        f.write('%s\n'%w)
    return

  save = w
  #if 1:
  try:

    # find the word
    record = soup.find('h1', attrs={'class':"keyword"}).text
    if record!=w:

        # we have already crawled this word
        if record in __VOCAB__:
          print "__existing__ ", w, record
          with codecs.open('pos_dict_dupl.txt', encoding='utf-8', mode='a') as fh:
            fh.write('%s\n'%w)
          return

        # ignore abbreviations
        if re.search('[A-Z][A-Z]', record):
          print "__abbreviation__ ", w, record
          with codecs.open('pos_dict_abbr.txt', encoding='utf-8', mode='a') as fh:
            fh.write('%s\n'%w)
          return

    if soup.find('div', attrs={'class':"ifufind"}):
      with codecs.open('pos_dict_unfound.txt', encoding='utf-8', mode='a') as fh:
        fh.write('%s\n'%w)
      print w, " - unfound"
      return

    save += '::' + record
    #print "word:", record

    # find POS
    div_pos = soup.find('div', attrs={'class':"basic clearfix"})
    li = div_pos.find('ul').find_all('li', recursive=False)
    pos = []
    for l in li:
      span  = l.find('span')
      if span: pos.append(span.text)
    save += '::' + ','.join(pos)

    # find different forms
    div_shape = soup.find('div', attrs={'class':"shape"})
    if div_shape:
        forms = []
        spans = div_shape.find_all('span')
        for s in spans:
            typ = s.find('label').text.strip(':')
            mut = s.find('a').text
            forms.append('%s:%s'%(typ, mut))
        save += '::' + ','.join(forms)
    print w, pos
    #print save

    __VOCAB__[record]=1

    with codecs.open('pos_dict.txt', encoding='utf-8', mode='a') as fh:
      fh.write('%s\n'%(save))

  #if 0:
  except Exception, err:
    print Exception, err
    with codecs.open('pos_dict_bad.txt', encoding='utf-8', mode='a') as fh:
      fh.write('%s\n'%w)
    print w, " !!! bad !!!"


# find the words that we already found
with open('pos_dict.txt', 'r') as f:
    for l in f:
        __VOCAB__[l.strip('\n').split('::')[0]]=1
        __VOCAB__[l.strip('\n').split('::')[1]]=1
with open('pos_dict_unfound.txt', 'r') as f:
    for w in f.readlines(): __VOCAB__[w.strip('\n')]=1
with open('pos_dict_bad.txt', 'r') as f:
    for w in f.readlines(): __VOCAB__[w.strip('\n')]=1
with open('pos_dict_badurl.txt', 'r') as f:
    for w in f.readlines(): __VOCAB__[w.strip('\n')]=1
with open('pos_dict_dupl.txt', 'r') as f:
    for w in f.readlines(): __VOCAB__[w.strip('\n')]=1
with open('pos_dict_abbr.txt', 'r') as f:
    for w in f.readlines(): __VOCAB__[w.strip('\n')]=1

print "%s entries in existing vocab ..."%len(__VOCAB__)

start=False
i=0
with open('wikiVocabulary.txt', 'r') as f:
 for l in f:
   i+=1
   fs = l.strip('\n').split('::')
   w, c = fs[0], fs[1]
   if not int(c) in [1, 2]: continue
   print i
   #raw_input()
   if w in __VOCAB__: continue
   if start==False:
       print w, c
       print "now starts ... (bypassing %s words)"%i
       raw_input()
   start=True
   crawl(w)
