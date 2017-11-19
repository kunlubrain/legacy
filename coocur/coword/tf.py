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

def pause(): raw_input('pause...')

def peek(steps, window):
    if steps%window==0: print "finished", steps, "files"

def __ignore(w):
    if re.search('^\d+$', w): return True

def wordlist(text, regular=True):
    words = re.findall('[\w-]+', text)                        # <--- !!! Wonderful
    return [w for w in words if not __ignore(w)]

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

def df_words():

    print "find df of words..."
    DF = {}
    for nFiles, text in enumerate(textFiles()):

        sentences = lang.getSentenceList(text)
        words = set(sum([wordlist(s, regular=True) for s in sentences], []))
        kbay.count(words, DF)

        peek(nFiles, 1000)

    print "finished total", nFiles, "files"
    kbay.saveDF(DF, SAVEDIR+SrcFileName+'_df.txt', sort=False, numDoc=nFiles)

# UNFINISHED, because the results of wiki is under "stats/wiki_word_coocur.txt"

