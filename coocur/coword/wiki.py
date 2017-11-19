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

if 0:
  s=__getSeeds()
  raw_input()

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

    #with codecs.open('dict.txt', encoding='utf-8', mode='a') as fh:
    #    fh.write(save)

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

def collect(words):
    for w in words:
        if not w in DF: DF[w]=0
        DF[w] += 1

DF={}

def cruchWikiText():

    seeds = __getSeeds()
    seeds = [s for s in seeds if not s in SEEDS_DOWNLOADED]

    patch_seeds = []

    global DF # explicit declaration, since we modify it after refer to it

    total = len(seeds)
    patch_num = 0
    print "save wiki text for %s pages"%(total)

    for seed in seeds:

      patch_seeds.append(seed)
      text = crawlWikiText(seed)
      words = tokenset(text)
      collect(words)
      filename = 'data/'+seed
      with codecs.open(filename, 'w', 'utf-8') as f:
        data = "%s\n%s"%(seed, text)
        f.write(data)

      if len(patch_seeds)%100==0:
        print "%s/%s"%(patch_num*1000+len(patch_seeds), total)

      # dump temp dict to a file
      if len(patch_seeds)%1000==0:

        print "dump for patch: dict size %s"%(len(DF))
        dumpfile = 'stats/wikiDFPatch_%s'%time.strftime("%Y_%m_%d_%H_%M")

        with codecs.open(dumpfile, 'w', 'utf-8') as f:
          f.write('::'.join(patch_seeds) + '\n')
          for word, count in DF.items():
              f.write('%s::%s'%(word, count)+'\n')

        # reset
        patch_seeds = []
        DF = {}
        patch_num += 1

def findAllSeedsDownloaded():
    ff = os.listdir('data')
    print "Exist %s seeds (text already downloaded)"%len(ff)
    return ff

DFComb = {}
DFDir = 'stats'

def combineDF():
    ff = os.listdir(DFDir)
    for f in ff:
        dffile = DFDir + '/' + f
        print "dffile", dffile
        with open(dffile, 'r') as fh:
            for line in fh:
                fields = line.split('::', 3)
                if not len(fields)==2: continue
                if not len(fields[0]): continue
                try:
                    word, count = fields[0], int(fields[1].strip('\n'))
                except:
                    print fields
                if re.search(r'[A-Z]', word): continue
                DFComb[word] = DFComb.get(word, 0) + count
                #raw_input('..')
        #raw_input('ok')
    with open('wikiDFComb.txt', 'w') as f:
        for word, count in DFComb.items():
            f.write('%s::%s\n'%(word,count))
    print "TOTAL DICT SIZE", len(DFComb)
    raw_input("all ok")

def checkDF():
    df = {}
    with open('wikiDFComb.txt', 'r') as f:
        for line in f:
            fields = line.split('::')
            df[fields[0]] = int(fields[1].strip('\n'))
    if 0:
        hist = {}
        for word, count in df.items():
            hist[count] = hist.get(count, 0) + 1
    histBin = {}
    for word, count in df.items():
        binnum = (count/1000)*1000
        histBin[binnum] = histBin.get(binnum, 0) + 1
    for key, count in sorted(histBin.items()):
        print key, " --> ", count

    for word, count in df.items():
        if count>1000 and count<2000:
            print word, " - ", count

    raw_input('break me')

def phraseMining(text):
    # mine phrase like 'pron' + 'noun' + 'pron'
    regexJieci = 'as,to,for,from,upon,in,at,of,with,on,out,outside,under,above,inside,within,onto,into,around,besides,near,about,along,by,between,through,over'
    regexJieci = regexJieci + ',before,after,behind,front,bottom,beneath'
    regexJieci = regexJieci + ',left,right'
    regexJieci = regexJieci + ',until,unless,still'
    regexArtical = 'the,a,an,these,those,this,that'
    regexPronoun = 'i,you,he,she,it,we,they,our,your,his,her,its,their,them,us,him'
    regexNumnoun = 'many,other,another,some,any,all,such,every,something,anythin,none,nothing'
    regexTempnoun = 'later,earlier,former,sooner,often,usally,always'
    regexCond = 'only,alone,not,both,or,very,ever,even,far,further'
    regexConj = 'if,whether,but,though,and,while,thus,hence,therefore,yet,moreover,including,consequently'
    # including is conjection + proverb
    regexCompare = 'like,more,less,few,fewer,most,least,better,worse,best,worst,than'
    regexQuestionHelper = 'where,what,who,why,when,which,whom'
    regexVerbHelper = 'has,have,be,is,are,been,being,having,was,were,do,does,did,done'
    regexModal = 'may,must,should,could,can,might'
    regexLocnount = 'here,there'
    regexStateAdv = 'really,indeed,also,merely,thouroughly,previously'

    stopwords = ','.join([regexJieci, regexArtical, regexPronoun, regexPronoun, regexTempnoun,
                          regexCompare, regexQuestionHelper, regexVerbHelper, regexModal,
                          regexLocnount, regexConj, regexConj, regexNumnoun, regexCond,
                          regexStateAdv])
    stopwords =  stopwords.split(',')
    #print stopwords

    regexStop = '|'.join([r'\b%s\b'%w for w in stopwords])
    #print "regexterms", regexStop

    regexJieci = regexJieci.replace(',', '|')
    regexPhrase = r'\b(%s)\s+(\w+)\s+(%s)\b'%(regexJieci, regexJieci)
    phrases = re.findall(regexPhrase, text)
    print "found phrases:", phrases

    print text
    # preprocessing - remove bad text
    text = re.sub('(?<=[a-z])\.(?=[A-Z])', '. ', text)

    #sentences = re.split('\.(?!\w)+', text)
    sentences = re.split('\.[^\w]+', text)

    for s in sentences:
        print '\n------------------', s
        if len(re.findall('\d+', s))>3:
            print "too many digits:"
            continue
        if not re.search('^[A-Z]', s):
            print "bad sentence - bad leading character"
            continue
        ngrams = re.split(regexStop, s)
        for g in ngrams:
            if len(g.split())==1:
                IGRAM_S[g] = IGRAM_S.get(g, 0) + 1

    raw_input('break me')

IGRAM_S = {}

def mineWiki():
    wikiTextFiles = os.listdir('data')
    for f in wikiTextFiles[:10]:
        print "mine file", f
        with open('data/'+f, 'r') as f:
            phraseMining(f.read())
    print IGRAM_S

mineWiki()
raw_input("DONE WIKI TEXT MINING")

#checkDF()

#combineDF()

# crunch()

# do this before downloading further seeds
SEEDS_DOWNLOADED = findAllSeedsDownloaded()

cruchWikiText()

