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

#-------
#<h3 style="left: 130px; position: absolute;" class="cur">英英释义</h3>
#<div class="layout en" style="display: block;">
#  <span>Noun:</span>
#   <ol style="overflow: hidden;">
#       <li>the ...; <p> "we were surprised by the extravagance of his description"<br> </p>
#  <span>Adjective:</span>
#   <ol style="overflow: hidden;">
#       <li>the ...; <p> "we were surprised by the extravagance of his description"<br> </p>
#       ...

def checkword(w):
    # english meanings
    save = 'W:%s'%w

    url="http://dict.cn/%s"%w
    soup = kutils.get_soup_retry(url, minsleep=3, maxretry=5)
    try:
        en = soup.find('div', attrs={'class':"layout en"})
        typew = en.find_all('span', recursive=False)
        for t in typew:
            typ = t.text.strip().strip(':')
            defs = t.find_next('ol')
            meanings = defs.find_all('li')
            meanings = [(trim(m.find('p').previousSibling), trim(m.find('p').text)) for m in meanings]
            save += " T:%s\n"%typ
            for m in meanings:
                save += "  M:%s\n"%m[0]
                save += "  E:%s\n"%m[1]
        with codecs.open('dict.txt', encoding='utf-8', mode='a') as fh:
            fh.write(save)
    except:
        save += 'ERR!!!'
        with codecs.open('dict_bad.txt', encoding='utf-8', mode='a') as fh:
            fh.write('%s\n'%w)

with open('58000_english_words.txt', 'r') as fh:
    words = fh.readlines()
    words = [trim(w) for w in words]

with open('dict_bad.txt', 'r') as fh:
    bad_words = fh.readlines()
    bad_words = [trim(w) for w in bad_words]

def crunch():
    for w in words[:]:
        checkword(w)


# CONSTRUCT THE WORD-BOOK
# WORD ->
#       TYPE ->
#           [ (MEANING, EXAMPLES) ]
# open the file of words
with open('dict.txt', 'r') as fh:
    text = fh.read()
# patterns
PttnWord='(W:\w+.*?\s+E:.*?)(?:W)'
PttnName='^W:(\w+)'
PttnType='(T:.*\n(\s+M:.*\n\s+E:.*\n)+)'

# chop out each word as a text block
blocks =re.findall(PttnWord, text, re.DOTALL)

wbook={}
for b in blocks[54:120]:
    word  = re.search(PttnName, b).group(1)
    wbook[word] = {}

    # chop out each type block
    types = re.findall(PttnType, b)

    for t in types:
        t = t[0]
        print t
        ty = re.search('^T:(\w+)', t).group(1)
        wbook[word][ty] = []

        # chop out each meaning using splitting
        t = t.replace('  M:', '#DELIM#  M:')
        meanings = t.split('#DELIM#')[1:]
        for m in meanings:
            meaning = re.search('\s+M:(.*)', m).group(1)
            example = re.search('\s+E:(.*)', m).group(1)
            wbook[word][ty].append((meaning, example))

for w in wbook:
    print w
    for t in wbook[w]:
        print "  ", t
        for x in wbook[w][t]:
            print "      ", x
