# -*- coding: utf-8 -*-
import re
import codecs
import os
import time

import lang
import kbay
import klog

import mine_wiki # for using "loopWikiData"
#import grammer

import memory

Records     = {}
SrcFileName = 'wiki'  # 'pmed'
SAVEDIR     = 'stats/wiki' # 'stats/pmed/'

def textFiles():
    return mine_wiki.loopWikiData()
    #fname = SrcFileName+'.txt'
    #print "load data from", fname
    #with open(fname, 'r') as f:
    #    for line in f:
    #        yield line

def pause(): raw_input('pause...')

def peek(steps, window):
    if steps%window==0: print "finished", steps, "files"

def __ignore(w):
    if re.search('^\d+$', w): return True

def wordlist(text, regular=True):
    words = re.findall('[\w-]+', text)                        # <--- !!! Wonderful
    return [w for w in words if not __ignore(w)]

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

def refreshMemory2D(hist, steps, prefilter):
    if prefilter:
        for w1, histOfW1 in hist.items():
            if hist[w1][w1] < steps * 0.0002:
                if hist[w1][w1] < 10:
                    hist.pop(w1)
    for w1 in hist:
        for w2, count in hist[w1].items():
            if count < hist[w1][w1] * 0.005:
                hist[w1].pop(w2)

        if len(hist[w1].items())>100:
            threshold = sorted(hist[w1].items(), key=lambda x:x[1])[-100][1]
            for w2, count in hist[w1].items():
                if count < threshold:
                    hist[w1].pop(w2)

def findNgrams(DO_COOCUR=False, ROUND=1):

    NGRAMS_DOC   = {}
    COOCUR_S     = {} # co-occurrence in a sentence
    NGRAM_LR     = {}

    for idx, text in enumerate(textFiles()):
        peek(idx+1, 1000)

        #if idx>1000: break

        ngram_local = {}
        sentences = lang.getSentenceList(text)

        for idofs, s in enumerate(sentences):

            tokenlist = lang.tokenize(s)
            poslist   = lang.posnize(tokenlist)

            #print "\n-----tokens and poslist----"
            #print ["(%s, %s)"%(t, poslist[i]) for i, t in enumerate(tokenlist)]

            if not len(tokenlist)>5:
                #print "Anormaly of sentence:", s
                #pause()
                continue

            tokenstoplist = lang.markStops(tokenlist)

            if 0:
                print "stops:"
                print tokenstoplist
                #pause()

            if len(tokenlist)>80:
                continue
                print "###### text ######", idx
                print text
                print tokenlist, len(tokenlist)
                #pause()

            ngb = lang.ngrambounds(tokenstoplist)
            #print "gram with bounds:", ngb

            selecedngb = lang.filterSRS(ngb, tokenstoplist)
            #print "\nSRS-FIL gram with bounds:", selecedngb
            selecedngb = lang.filterAdj(selecedngb, s)
            #print "\nADJ-FIL gram with bounds:", selecedngb
            selecedngb = lang.filterAdv(selecedngb, s)
            #print "\nADV-FIL gram with bounds:", selecedngb
            #selecedngb = lang.filterVerb(selecedngb, s, verbose=0) #<--- "contrast", "field" incorrectly ignored
            #print "\nVERB-FIL gram with bounds:", selecedngb

            # do it again after pure pos-based filtering
            selecedngb = lang.filterSRS(selecedngb, tokenstoplist)
            #print "\nFINAL selected gram with bounds:", selecedngb


            if ROUND==1:
              # in the 1st round, profile the next word after a gram
              for (gram, leftidx, rightidx) in selecedngb:
                  nextword = lang.nextword(rightidx, tokenlist)
                  prevword = lang.prevword(leftidx, tokenlist)
                  nextwordcode = lang.profilingCode(nextword)
                  prevwordcode = lang.profilingCode(prevword)

                  kbay.inc3d(gram, '_', '_', NGRAM_LR)  # '_' as itself
                  kbay.inc3d(gram, 'l', prevwordcode, NGRAM_LR)
                  kbay.inc3d(gram, 'r', nextwordcode, NGRAM_LR)

                  if lang.isSubject(leftidx, rightidx, tokenlist):
                    kbay.inc3d(gram, '_', 's', NGRAM_LR)
                    #print "subject:", gram
                    #pause()

            if ROUND==2:
              # in the 2nd round, justify the gram
              for ngb in selecedngb:
                  print "check this:", ngb
                  sg = grammer.subgram(ngb[0], ngb[1], ngb[2], READIN_GRAM_LR, tokenlist, poslist)
                  if sg:
                    print "gram", ngb, "subgram", sg
                    raw_input()

            if 0:
                print "\n\n", s
                print "raw   ngb >", ngb
                print "final ngb >", selecedngb
                pause()

            ngrams = [t[0] for t in selecedngb]
            ngrams = [g for g in ngrams if len(g.split())>1]

            kbay.count(ngrams, ngram_local)

            if DO_COOCUR:
              for n1 in ngrams:
                  for n2 in ngrams:
                      kbay.inc2d(n1, n2, COOCUR_S)

        # doc.freq. - each gram counted only once
        kbay.count(ngram_local, NGRAMS_DOC)

    kbay.saveHist3D(NGRAM_LR, SAVEDIR+'hist.txt')

    #print "filter df-doc"
    #filterHistByCount(NGRAMS_DOC, 2, verbose=False)
    #kbay.saveDF(NGRAMS_DOC,   SAVEDIR+SrcFileName+'_ngrams_df_doc.txt', sort=False, numDoc=idx)

    if DO_COOCUR:
      print "filter coocur"
      kbay.filter2DHistByCount(COOCUR_S, 2, verbose=True)
      kbay.saveDF2D(COOCUR_S, SAVEDIR+SrcFileName+'_ngrams_coocur.txt')

    print "DONE findNgrams"

def findDFOfWords():

    print "find df of words..."
    DF = {}
    for nFiles, text in enumerate(textFiles()):

        sentences = lang.getSentenceList(text)
        words = set(sum([wordlist(s, regular=True) for s in sentences], []))
        kbay.count(words, DF)

        peek(nFiles, 1000)

    print "finished total", nFiles, "files"
    kbay.saveDF(DF, SAVEDIR+SrcFileName+'_df.txt', sort=False, numDoc=nFiles)

# co-occur of two words in a sentence
def coocurWordFirstOrder():

    klog.msg('find word coocur')
    Hist = {}
    nNumSentences=0
    for nFiles, text in enumerate(textFiles()):
        sentences = lang.getSentenceList(text)
        nNumSentences += len(sentences)
        if nFiles>100000: break
        if nFiles%1000==1:
            print nFiles, " files: #.sentences", nNumSentences
        continue
        for ids, s in enumerate(sentences):
            tokenlist = lang.tokenize(s)
            tokenlist = lang.regularwords(tokenlist)
            selected = [t for t in tokenlist if not lang.isNoise(t)]
            #kbay.countCooccur(selected, Hist)
            kbay.countCooccurNearest(selected, Hist, nearest=10)

        if nFiles%1000==1:
            refreshMemory2D(Hist, steps=nFiles, prefilter=True)
            h, hh = len(Hist), kbay.sizeOf2DHist(Hist)
            print "hist size", h, hh, hh/h
        peek(nFiles+1, 1000)
        if nFiles>100000: break
    print "number of sentences:", nNumSentences
    return
    klog.msg("finished total %s files"%nFiles)
    refreshMemory2D(Hist, steps=nFiles, prefilter=True)
    kbay.filter2DHistByCount(Hist, 3, verbose=True)
    kbay.saveDF2D(Hist, SAVEDIR+SrcFileName+'_word_coocur.txt')

def rank():
    klog.msg('rank words in text based on cross-info score')
    for nFiles, text in enumerate(textFiles()):
        sentences = lang.getSentenceList(text)
        wordprof = {}
        wordscores = []
        print "############ TEXT #############"
        print text
        for ids, s in enumerate(sentences):
            tokenlist = lang.tokenize(s)
            tokenlist = lang.regularwords(tokenlist)
            selected = set([t for t in tokenlist if not lang.isNoise(t)])
            for w in selected: wordprof[w] = wordprof.get(w, 0) + 1
            print s
            for w in selected:
                s = memory.sumscore([ww for ww in selected if ww!=w], w)
                wordscores.append((w,s))
            print sorted(wordscores, key=lambda x:x[-1], reverse=True)
            wordscores = []
            pause()

        #wordset = wordprof.keys()
        #for w, count in wordprof.items():
        #    s = memory.sumscore([ww for ww in wordset if ww!=w], w)
        #    wordscores.append((w,count,s))
        #print sorted(wordscores, key=lambda x:x[-1], reverse=True)
        #pause()

coocurWordFirstOrder()
#rank()

# 1. df df of individual words (1-gram)
#findDFOfWords()

# 2. count of ngrams
#findNgrams(DO_COOCUR=False, ROUND=1)
