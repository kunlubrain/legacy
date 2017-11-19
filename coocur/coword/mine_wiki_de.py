# -*- coding: utf-8 -*-
import re
import kutils
import codecs
import os
import time

import lang_cleaner as cleaner
import mine_helper_fif
import memoryRefresh
import coocur
import klog
import kbay
import fif
import nlp

def pause(): raw_input('pause...')

def loopWikiData():
    datafiles = os.listdir('data_wiki_de')
    for datafile in datafiles:
        fname = 'data_wiki_de/' + datafile
        with open(fname, 'r') as fh:
            text =  fh.read()
            yield datafile, text

TotalWordCount = 0
GlobalHist     = {}
WordCount      = {}

def countDF(verbose=0):

    TotalWordCount = 0
    GlobalHist     = {}
    WordCount      = {}

    for idx, (datafile, text) in enumerate(loopWikiData()):
        sentences = cleaner.getSentences(text)

        localHist = {}

        for s in sentences:
            if verbose:
                print "#############"
                print s
            words = s.split()
            for w in words:
                localHist[w] = localHist.get(w, 0) + 1
            TotalWordCount += len(words)

        for w in localHist:
            GlobalHist[w] = GlobalHist.get(w, 0) + 1
            WordCount[w] = WordCount.get(w, 0) + 1

        if idx%1000==0:
            print "finished", idx, "files"
            print "TotalWordCount ", TotalWordCount
            print "VolcabSize     ", len(WordCount.keys())

        #if idx>500: break

    mine_helper_fif.saveWordFreq(WordCount, TotalWordCount, 'WordFreq.txt')
    mine_helper_fif.saveWordFreq(GlobalHist, idx, 'WordDF.txt')


# Find related words by constructing a 2-d hist for words occurred in the same
# sentence.
def nearalation():
    for idx, (datafile, text) in enumerate(loopWikiData()):
        sentences = cleaner.getSentences(text)
        for s in sentences:
            tokens = cleaner.tokenize(s)
            print tokens
            pause()

def coocurWord(save2file, verbose=0):
    klog.msg('find word coocur')
    Hist = {}
    for nFiles, (datafile, text) in enumerate(loopWikiData()):
        sentences = cleaner.getSentences_regex(text)
        for s in sentences:
            #selected = set(cleaner.capitalizedWordsOf(s))
            selected = cleaner.tokenize_simple(s)
            if verbose or 0:
                print "sentence:", s
                print "selected:", selected
                pause()
            #kbay.countCooccurNearest(selected, Hist, nearest=10)
            kbay.countCooccurNearest(selected, Hist, nearest=2)
            #print "learn", selected
            #print Hist, len(Hist)
            #pause()
        if nFiles%1000==0: print nFiles, " files done"
        if nFiles%4000==0:
            print "before mem refresh:", len(Hist)
            memoryRefresh.refreshMemory2D(Hist, steps=nFiles, prefilter=True)
            print "after mem refresh:", len(Hist), '\n'
        if nFiles>40000: break

    klog.msg("finished total %s files"%nFiles)
    memoryRefresh.refreshMemory2D(Hist, steps=nFiles, prefilter=True)
    kbay.filter2DHistByCount(Hist, 3, verbose=True)

    fif.saveHist2D(Hist, save2file)

    return Hist


# 1. countDF()
# 2. mine_helper_converter

# 3. redo
#nearalation()

#cohist = coocurWord(save2file='stats/wiki_de_word_coocur', verbose=0)
cohist = coocurWord(save2file='stats/wiki_de_word_coocur_leftright', verbose=0)
cohist = coocur.forget(cohist)
fif.saveHist2D(cohist, 'stats/wiki_word_coocur_filtered.txt')
