# -*- coding: utf-8 -*-

import re
import codecs

def saveTF(WFHist, totalWordCount, fname):

    #with codecs.open(fname, 'w', encoding="utf-8") as fh:
    with open(fname, 'w') as fh:
        for k, c in WFHist.items():
            fh.write('%s::%d::%f\n'%(k, c, float(c)/totalWordCount))
    print "[DONE] Saved to", fname, "len=", len(WFHist)

def saveHist3D(hist, fname):
    with open(fname, 'w') as fh:
        for i, h in hist.items():
            for ii, hh in h.items():
                for iii, cnt in hh.items():
                    fh.write("%s::%s::%s::%s\n"%(i,ii,iii,cnt))
    print "[DONE] Saved to", fname, "len=", len(hist)

def saveHist4D(hist, fname):
    x = 0
    with open(fname, 'w') as fh:
        for i, h in hist.items():
            for ii, hh in h.items():
                for iii, hhh in hh.items():
                    for iiii, cnt in hhh.items():
                        fh.write("%s::%s::%s::%s::%s\n"%(i,ii,iii,iiii,cnt))
                        x += 1
    print "[DONE] Saved to", fname, "len=", len(hist), "size=", x

def saveHist2D(hist, fname, splitter='::'):
    #with codecs.open(fname, 'w', encoding="utf-8") as fh:
    with open(fname, 'w') as fh:
        for i, x in hist.items():
            for ii, cnt in x.items():
                fh.write("%s%s%s%s%s\n"%(i,splitter, ii, splitter, cnt))
    print "[DONE] Saved to", fname, "len=", len(hist), ":", sum([len(h) for k,h in hist.items()])

def readTF(fname, tf={}, threshold=0):
    print "fif: read term-freq from", fname
    with open(fname, 'r') as fh:
        for i, line in enumerate(fh):
            fields = line.strip('\n').split('::')
            try: word, count = fields[0], int(fields[1])
            except: continue
            if count>threshold:
                tf[word] = count
    return tf

def readWithFilter(fname, filtervalue):
    print "fif: read from", fname, "filter by", filtervalue
    book = {}
    with open(fname, 'r') as fh:
        for i, line in enumerate(fh):
            fields = line.strip('\n').split('::')
            word1, count = fields[0], int(fields[1])
            if count >= filtervalue:
                book[word1] = count
            if i%100000==0: print "finished %s lines"%i
    return book

def readCTF3(fname, filtervalue):
    print "fif: read conditional-tf-3d from", fname
    hist = {}
    with open(fname, 'r') as fh:
        for line in fh:
            words = line.strip('\n').split('::')
            w1, w2, w3, count = words[0], words[1], words[2], int(float(words[3]))
            if count>=filtervalue:
                if not w1 in hist: hist[w1]={}
                if not w2 in hist[w1]: hist[w1][w2]={}
                if not w3 in hist[w1][w2]: hist[w1][w2][w3]=count
    return hist

def readWordCoocur(fname, filtervalue=0):
    print "fif: read word coocur from", fname
    book = {}
    with open(fname, 'r') as fh:
        for line in fh:
            fields = line.strip('\n').split('::')
            word1, word2, count = fields[0], fields[1], int(float(fields[2]))
            if count>=filtervalue:
                if not word1 in book: book[word1] = {}
                book[word1][word2] = int(count)
    return book

def readCoocurWithFilterFunc(fname, dfbook, filtervalue=2):
    print "fif: read word coocur from", fname
    book = {}
    with open(fname, 'r') as fh:
        for i, line in enumerate(fh):
            #if i>1e6: break
            fields = line.strip('\n').split('::')
            word1, word2, count = fields[0], fields[1], int(float(fields[2]))
            if not word1 in book:
                book[word1] = {}
            #if count==1 and dfbook.get(word2,0) * len(word2.split()) < 10:
            if count==1:
                #print "filter out:", word1, "/", word2, count
                #raw_input()
                continue
            if count>=filtervalue:
                book[word1][word2] = int(count)
            if i%500000==0: print "finished %s lines"%i
    return book

def readMakeId(fname, dfbook, filtervalue=2):
    book     = {}
    id2term  = {}
    term2id  = {}
    nextid   = 1
    def __idOfWord(word, term2id, nextid):
        if not word in term2id:
            term2id[word] = nextid
            word_id       = nextid
            nextid        += 1
        else:
            termid        = term2id[word1]
        return termid, nextid

    with open(fname, 'r') as fh:
        for i, line in enumerate(fh):
            fields = line.strip('\n').split('::')
            word1, word2, count = fields[0], fields[1], int(float(fields[2]))
            word1_id, nextid = __idOfWord(word1, nextid)
            word2_id, nextid = __idOfWord(word2, nextid)
            if not word1_id in book: book[word1] = {}
            if count==1: continue
            if count>=filtervalue: book[word1][word2] = int(count)
            if i%500000==0: print "finished %s lines"%i
    return book

def readWordCoocurInplace(fname, book):
    print "reading coocur from", fname
    with open(fname, 'r') as fh:
        for line in fh:
            fields = line.strip('\n').split('::')
            word1, word2, count = fields[0], fields[1], int(fields[2])
            book[word1] = book.get(word1, {})
            book[word1][word2] = book[word1].get(word2,0) + int(count)

def readWordCoocurFilter(fname, book):

    print "reading coocur from", fname
    localdict = {}

    with open(fname, 'r') as fh:
        for idx, line in enumerate(fh):
            fields = line.strip('\n').split('::')
            word1, word2, count = fields[0], fields[1], int(fields[2])

            if not word1 in localdict:

                # check and record the localdict
                for localseed in localdict:
                    assert len(localdict)==1
                    seedcount = localdict[localseed][localseed]
                    if not seedcount>2: continue
                    for w, count in localdict[localseed].items():
                        book[word1] = book.get(word1, {})
                        book[word1][w] = book[word1].get(w,0) + int(count)

                # reset for new localdict
                localdict = {}
                localdict[word1] = {}
                localdict[word1][word2] = count

            else:
                localdict[word1][word2] = localdict[word1].get(word2,0) + int(count)

            if idx%100000==0:
                print "finished %s lines"%idx
                print "dict size:%s"%len(book)

def readWordCoocurInplaceFilterByInitial(fname, book, initial):
    with open(fname, 'r') as fh:
        for line in fh:
            if not re.search(r'^%s'%initial, line): continue
            fields = line.strip('\n').split('::')
            word1, word2, count = fields[0], fields[1], int(fields[2])
            book[word1] = book.get(word1, {})
            book[word1][word2] = book[word1].get(word2,0) + int(count)

def readDFAsRatioFromFile(fname, indexOfRatio):
    print "read df from", fname
    book = {}
    with open(fname, 'r') as fh:
        for line in fh:
            fields = line.strip('\n').split('::')
            word, count, ratio = fields[0], fields[1], fields[indexOfRatio]
            book[word] = float(ratio)
    return book

def readDFAsCountFromFile(fname, validation=True):

    book = {}
    with open(fname, 'r') as fh:
        for line in fh:
            fields = line.strip('\n').split('::')
            word, count = fields[0], fields[1]

            if validation:
                if re.search(r'[A-Z]', word): continue
                if re.search(r'\d', word): continue
                if re.search(r'\W', word, re.UNICODE): continue

            book[word] = count

    return book

generateDFRatioFromCount = 0
if generateDFRatioFromCount:
  dfwiki = readDFAsCountFromFile('wikiDFComb.txt')
  dfieee = readDFAsCountFromFile('ieee/stat/ieee_ALL_df.txt')

  with open('statDFWord_Wiki.txt', 'w') as f:
      for w, c in dfwiki.items():
          ratio = float(c)/690000
          f.write("%s::%s::%s\n"%(w,c,ratio))

  with open('statDFWord_Ieee.txt', 'w') as f:
      for w, c in dfieee.items():
          ratio = float(c)/460036
          f.write("%s::%s::%s\n"%(w,c,ratio))

test=0
if test:
  dfieee = readDFAsRatioFromFile('statDFWord_Ieee.txt', indexOfRatio=2)
  dfcros = readDFAsRatioFromFile('stats/pmed/pmed_df.txt', indexOfRatio=-1)
  #dfcros = readDFAsRatioFromFile('statDFWord_Wiki.txt', indexOfRatio=2)

  print "len df ieee", len(dfieee)
  print "len df cros", len(dfcros)

  threshold = 0.001
  threshold = 10.0/460036
  i=0
  for w, r in dfieee.items():
      r2 = dfcros.get(w, 0)
  #for w, r in dfcros.items():
  #    r2 = dfieee.get(w, 0)
      #if r > r2*0.5 and r<r2*2 and r>threshold:
      #if r>threshold:
      #if r*10 < r2:
      #if r>threshold and r>r2*10 and r2!=0:
      if r>0.005 and r>10*r2:
          raw_input("%s %s %s count= %s"%(w, r, r2, r*460036))
          i+=1
  print i
