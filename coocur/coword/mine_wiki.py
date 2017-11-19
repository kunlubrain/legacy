# -*- coding: utf-8 -*-
import re
import kutils
import codecs
import os
import time

import lang
import lang_cleaner as cleaner

import langHardStop
HardStop = langHardStop.HardStop

Records = {}
DFDir = 'stats'

def pause(): raw_input('pause...')

def _saveDF2File(df, fname, sort=False):
    pairs = sorted(df.items(), key=lambda x:x[1], reverse=True) if sort else df.items()
    with open(fname, 'w') as f:
        for word, count in pairs:
            f.write('%s::%s\n'%(word,count))
    print "DONE - save df file", fname, "size=", len(df)

def _saveHist2D(hist, fname):
    with open(fname, 'w') as f:
      for word1 in hist:
        for word2, count in hist[word1].items():
            f.write('%s::%s::%s\n'%(word1, word2, count))
    print "DONE - save 2d-hist file", fname

def _loadDFFrom(fname):
    df = {}
    with open(fname, 'r') as f:
        for line in f:
            fields = line.split('::')
            word, count = fields[0], int(fields[1].strip('\n'))
            df[word] = count
    return df

def tokenize(text):
    words = re.findall('\w+', text)
    return words

def cleanWikiText(text):
    # remove references
    pass

def getSentences(text):
    def _delimit(m): return '#!*'+m.group(1).strip()
    def _good(s):
        l = len(s.split())
        if l<6: return False
        if l>60: return False
        if not re.search(r'^[A-Z]', s): return False
        return True
    def _lower(m): return m.group(0).lower()
    def _split(m): return '. ' + m.group(1)

    text = re.sub(r'\[[\d\W]+\]', '', text) # remove references like [38]
    text = re.sub(r'\[.{0,30}\]', '', text) # remove references like [by whom?]
    text = re.sub(r'\(.*?\)', '', text) # remove noisy brackets
    text = re.sub(r'".*?"', '', text) # remove noisy quotations
    text = re.sub(r'([A-Z]\.\s*)+', 'X', text) # remove acronym of person's name
    text = re.sub('(?<=[a-z])([A-Z])(?=[a-z])', _split, text) # handle 'fooBar is a ...'

    text = re.sub('\.+\s+([A-Z])', _delimit, text) # standard pattern: word. A-Z
    text = re.sub('(?<=[\w\s])\.+([A-Z])', _delimit, text) # missing space: word.A-Z
    text = re.sub('\s*:\s*([A-Z])', _delimit, text) # break at the column

    sentences = text.split('#!*')
    sentences = [re.sub('^(\w+)', _lower, s) for s in sentences if _good(s)]
    #for s in sentences: print "> ", s

    return sentences

def wordlist(text):
    return re.findall('[\w-]+', text)                        # <--- !!! Wonderful

def tokenset(text):
    def __splitting(mo): return ' '+mo.group(0)
    def __lowering(mo): return mo.group(0).lower()
    def _good(w): return not (re.search(r'\d', w) or re.search(r'_',w))

    # split the text like 'fooBar is', where punctuation lost between'foo' and 'Bar'
    # in Regex [a-z]{2}: look behind requiring fix lenghth, use 2 as lower bound
    text = re.sub(r'(?<=[a-z]{2})[A-Z]', __splitting, text)
    text = re.sub(r'[^\w\s]\s*[a-z]', __lowering, text)
    words = set(re.findall('\w+', text))                        # <--- !!! Wonderful
    return [w for w in words if _good(w)]

def collect(words, DF):
    for w in words:
        if not w in DF: DF[w]=0
        DF[w] += 1

def loopWikiData():
    datatiles = os.listdir('data_wikitiles')
    for t in datatiles:
        tiledir = 'data_wikitiles/%s/'%t
        datafiles =  os.listdir(tiledir)
        for datafile in datafiles:
            fname = tiledir + datafile
            with open(fname, 'r') as fh:
                text =  ''.join(fh.readlines()[1:])
                yield text

def showSize2D(hist, histname):
    def _lenHist2D(hist):
        size = 0
        for w1 in hist:
            for w2, count in hist[w1].items():
                size+=count
        return size
    print histname, ": size=", _lenHist2D(hist)

def showSize(hist, histname):
    print histname, ": size=", len(hist)

def refreshMemory(hist, steps):
    def _thresh1Gram():
        return 1 if steps<=8000 else 2 if steps<=12000 else 3 if steps<=16000 else 4
    def _threshNGram():
        return 1 if steps<=20000 else 2

    threshold = 1 if steps<=8000 else 2 if steps<=12000 else 3 if steps<=16000 else 4
    for ng, count in hist.items():
        if len(ng.split())==1: threshold = _thresh1Gram()
        else: threshold = _threshNGram()
        if count<threshold:
            hist.pop(ng)

def refreshMemory2D(hist, steps):
    for w1, histOfW1 in hist.items():
        if hist[w1][w1] < steps * 0.001:
            hist.pop(w1)
    for w1 in hist:
        for w2, count in hist[w1].items():
            if count < hist[w1][w1] * 0.05:
                hist[w1].pop(w2)

def filterByCount(df, level):
    for gram, count in df.items():
        if not count>=level:
            df.pop(gram)

def _ignore(w):
        if w in HardStop: return True
        if re.match('\d+', w): return True
        if len(w)<2: return True

def findNgrams():

    NGRAMS_DOC = {}
    NGRAMS_TOTAL = {}

    COOCUR_S = {} # co-occurrence in a sentence
    DO_COOCUR =  False

    nfiles = 0
    nPass = 0

    __USE_OLD_CODE = 0
    __POSTERIOR__ = {}

    print "start doing ngram ..."

    for text in loopWikiData():

        nPass+=1
        if nPass<=100000: continue
        if nPass==100001: print "start couting ..."

        if __USE_OLD_CODE:

          nfiles+=1
          if nfiles%500==0: print "finished",nfiles,"files"
          if nfiles%10000==0:
              showSize(NGRAMS_DOC,   "%s ng-doc vor-refresh"%nfiles)
              refreshMemory(NGRAMS_DOC, nfiles)
              showSize(NGRAMS_DOC,   "%s ng-doc nach-refresh"%nfiles)
              showSize(NGRAMS_TOTAL, "%s ng-total vor-refresh"%nfiles)
              refreshMemory(NGRAMS_TOTAL, nfiles)
              showSize(NGRAMS_TOTAL, "%s ng-total nach-refresh"%nfiles)

              if DO_COOCUR:
                showSize2D(COOCUR_S,   "%s coocur vor-refresh"%nfiles)
                refreshMemory2D(COOCUR_S, nfiles)
                showSize2D(COOCUR_S,   "%s coocur nach-refresh"%nfiles)
              #pause()
          if nfiles>100000: break

        if not __USE_OLD_CODE:
          nfiles+=1
          if nfiles%1000==0: print "finished",nfiles,"files"
          if nfiles>200000: break

        sentences = getSentences(text)
        ngram_doc = {}
        for s in sentences:
          s = re.sub('[,:]', ' ,', s)
          s = re.sub("'s", " 's", s)  # remove stuff like: foo's
          s = re.sub("\s+", " ", s)  # remove stuff like: foo's

          # new code to get the posterior distribution
          sentenceParts = re.split('[,:]', s)

          for ss in sentenceParts:
            words =  ss.strip().split()
            for idx, w in enumerate(words[:-1]):
                if re.search('[\W\d]', w): continue
                if re.search('[A-Z][A-Z]', w): continue
                nextword = words[idx+1]
                if not w in __POSTERIOR__: __POSTERIOR__[w]={}
                __POSTERIOR__[w][w] = __POSTERIOR__[w].get(w,0) + 1
                if re.search('[\W\d]', nextword): continue
                if re.search('[A-Z][A-Z]', nextword): continue
                __POSTERIOR__[w][nextword] = __POSTERIOR__[w].get(nextword,0) + 1

            if __USE_OLD_CODE:
              # old code to get the ngrams
              words = wordlist(ss.strip())
              words = ['# ' if _ignore(w) else w+' ' for w in words]
              ngrams = [n.strip() for n in re.split('# ', ''.join(words)) if n]

              for n in ngrams: NGRAMS_TOTAL[n]=NGRAMS_TOTAL.get(n, 0)+1
              for n in ngrams: ngram_doc[n]=1

              if DO_COOCUR:
                for n1 in ngrams:
                    for n2 in ngrams:
                        COOCUR_S[n1] = COOCUR_S.get(n1, {})
                        COOCUR_S[n1][n2] = COOCUR_S[n1].get(n2, 0) + 1

          if 0:
           print "sentence > ", s
           print "sent-par > ", sentenceParts
           print "posterior > ", __POSTERIOR__
           raw_input()

        if __USE_OLD_CODE:
          # only for this doc
          for n in ngram_doc: NGRAMS_DOC[n] = NGRAMS_DOC.get(n,0)+1

    _saveHist2D(__POSTERIOR__, 'wikiPosterior.txt')

    if __USE_OLD_CODE:
      # save results
      refreshMemory(NGRAMS_DOC, nfiles)
      refreshMemory(NGRAMS_TOTAL, nfiles)
      _saveDF2File(NGRAMS_DOC, 'ngrams_df_doc_30w_40w.txt')
      _saveDF2File(NGRAMS_TOTAL, 'ngrams_total_count_30w_40w.txt')

      if DO_COOCUR:
        _saveHist2D(COOCUR_S, 'ngrams_coocur_10w.txt')

      print "DONE findNgrams"

def __goodword(w): return re.match(r'^[a-zA-Z]+$', w)

def countWordFreq():
    WordBook = {}
    GramBook = {}
    TotalCnt = 0
    for idx, text in enumerate(loopWikiData()):
        sentences = getSentences(text)
        for s in sentences:

            words = lang.tokenize(s)
            words = [w if(__goodword(w)) else ',' for w in words]

            # count single word
            for w in words: WordBook[w] = WordBook.get(w, 0) + 1
            TotalCnt += len(words)

            # count 2-gram
            tokenstoplist = lang.markStops(words)
            ngb = lang.ngrambounds(tokenstoplist)
            for (gram, leftidx, rightidx) in ngb:
                if rightidx > leftidx:
                    for ii in range(rightidx-leftidx):
                        twogram = words[leftidx+ii]+' '+words[leftidx+ii+1]
                        GramBook[twogram] = GramBook.get(twogram, 0) + 1
        if idx%1000==0: print "finished",idx,"files"
        if idx==100000: break

    SaveFile='wiki_WordFreq.txt'
    with codecs.open(SaveFile, 'w', 'utf-8') as f:
        for word, count in WordBook.items():
            f.write('%s::%s\n'%(word, count))
        f.write('#TOTAL_NUMBER_OF_WORDS=%s'%TotalCnt)
    with codecs.open('wiki_GramFreq.txt', 'w', 'utf-8') as f:
        for word, count in GramBook.items():
            f.write('%s::%s\n'%(word, count))
    print "dict size %s, saved to %s"%(len(WordBook), SaveFile)

def countDFOfTiles():

    datatiles = os.listdir('data_wikitiles')
    for t in datatiles:

        DF = {}

        tiledir = 'data_wikitiles/%s/'%t
        datafiles =  os.listdir(tiledir)

        print "%d files in tile %s"%(len(datafiles), t)

        for datafile in datafiles:
            fname = tiledir + datafile
            with open(fname, 'r') as fh: text =  ''.join(fh.readlines()[1:])
            words = tokenset(text)
            if 0:
              print fname
              print text
              print "> tokens\n", words
              print "> sometoken\n", [w for w in words if re.search(r'^[A-Z]', w)]
              raw_input('next')
            collect(words, DF)

        dumpfile = 'stats/%s'%t
        with codecs.open(dumpfile, 'w', 'utf-8') as f:
          for word, count in DF.items():
              f.write('%s::%s\n'%(word, count))

        print "dict size %s"%(len(DF))
        print "saved to", dumpfile
        #raw_input('breakme')

def combineDF():
    DFComb = {}
    ff = os.listdir(DFDir)
    for f in ff:
        dffile = DFDir + '/' + f
        print "dffile", dffile
        with open(dffile, 'r') as fh:
            for line in fh:
                fields = line.split('::')
                word, count = fields[0], int(fields[1].strip('\n'))
                DFComb[word] = DFComb.get(word, 0) + count

    _saveDF2File(DFComb, 'wikiDFComb.txt')

    print "TOTAL DICT SIZE", len(DFComb)
    raw_input("combineDF all ok")

def regularizeDF():
    df = _loadDFFrom('wikiDFComb.txt')
    for word, count in df.items():
        if re.search('[A-Z]', word): df.pop(word)
        if re.search('\W', word, re.UNICODE): df.pop(word)

    print "after regularization:"
    print "dict size:", len(df)
    _saveDF2File(df, 'wikiDFRegular.txt')

    # select the words with df > 10-e5
    for word, count in df.items():
        if not count>6: df.pop(word)

    print "after selection"
    print "dict size:", len(df)
    _saveDF2File(df, 'wikiDFUseful.txt')

    # classifiy the words into groups based on DF
    if 0:
      histBin = {}
      for word, count in df.items():
          binnum = (count/1000)*1000
          histBin[binnum] = histBin.get(binnum, 0) + 1
      for key, count in sorted(histBin.items()):
          print key, " --> ", count

    print "DONE regularization"

# Select from DF those above certain level
def selectDF():

    df = _loadDFFrom('wikiDFUseful.txt')
    selected = {}
    for w, c in df.items():
        if c > 10000: selected[w] = c
    _saveDF2File(selected, 'wikiDF_10000.txt', sort=True)

    selected = {}
    for w, c in df.items():
        if c>5000 and c<10000: selected[w] = c
    _saveDF2File(selected, 'wikiDF_5000_10000.txt', sort=True)

    selected = {}
    for w, c in df.items():
        if c>=69000: selected[w] = c
    _saveDF2File(selected, 'wikiDF_69000.txt', sort=True)

def phraseMining(text):
    # mine phrase like 'pron' + 'noun' + 'pron'

    stopwords =  "load stop words"

    regexStop = '|'.join([r'\b%s\b'%w for w in stopwords])

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
        print "ngrams:", ngrams

    raw_input('break me')

IGRAM_S = {}

def mineWiki():
    tiles = os.listdir('data_wikitiles')
    for t in tiles:
        wikiTextFiles = os.listdir('data_wikitiles/'+t)

        for f in wikiTextFiles[:10]:
            print "mine file", f
            with open('data_wikitiles/'+t+'/'+f, 'r') as f:
                phraseMining(f.read())
        print IGRAM_S


def posthist(condition):
    hist, hist_ngram = {}, {}
    hist_red, hist_ngram_red = {}, {}
    hist_light, hist_ngram_light = {}, {}
    for i, text in enumerate(loopWikiData()):
        sentences = cleaner.getSentences(text)
        for sent in sentences:
            sent = sent.lower()
            sent = re.sub("[,:']", ' the ', sent)
            samples = re.findall('\w+', sent)


            # if not sum(word in samples for word in condition)==len(condition): continue
            # for word in samples: hist[word] = hist.get(word, 0) + 1
            # ngrams = (' '.join(['#' if _ignore(w) else w for w in samples])).split('#')
            # ngrams = [n.strip() for n in ngrams if n]
            # for ng in ngrams: hist_ngram[ng] = hist_ngram.get(ng, 0) + 1

            if not "red" in samples:
                if not "light" in samples: continue

            ngrams = (' '.join(['#' if _ignore(w) else w for w in samples])).split('#')
            ngrams = [n.strip() for n in ngrams if n]

            if "red" in samples:
                for word in samples: hist_red[word] = hist_red.get(word, 0) + 1
                for ng in ngrams: hist_ngram_red[ng] = hist_ngram_red.get(ng, 0) + 1
            if "light" in samples:
                for word in samples: hist_light[word] = hist_light.get(word, 0) + 1
                for ng in ngrams: hist_ngram_light[ng] = hist_ngram_light.get(ng, 0) + 1

            #print "sentence matching full condition:", sent
            #print "ngrams:", ngrams
            #raw_input()

        #if i%1000==0: print "finished %s files"%i, "hist size=", len(hist)
        if i%1000==0: print "finished %s files"%i, "len_red=", len(hist_red), "len_red_ng=", len(hist_ngram_red), "len_light", len(hist_light), "len_light_ng=", len(hist_ngram_light)
        if i>100000: break

    #_saveDF2File(hist, 'wikiConditionHist_red_light.txt', sort=True)
    #_saveDF2File(hist_ngram, 'wikiConditionHistNgram_red_light.txt', sort=True)
    _saveDF2File(hist_red, 'wikiConditionHist_red.txt', sort=True)
    _saveDF2File(hist_ngram_red, 'wikiConditionHistNgram_red.txt', sort=True)
    _saveDF2File(hist_light, 'wikiConditionHist_light.txt', sort=True)
    _saveDF2File(hist_ngram_light, 'wikiConditionHistNgram_light.txt', sort=True)

#1. calculate DF for each wiki-text tile
#countDFOfTiles()

#2. calculate the combined-DF from the tile-DF calculated in step-1
#combineDF()

#3. clean and filter based on word form and df
#regularizeDF()

#4. select and save a part of the words whose df within certain range
#selectDF()

#5. mine the n-gram phrases in wiki-text
#mineWiki()

#findNgrams()

#countWordFreq()

posthist(condition=["red", "light"])
