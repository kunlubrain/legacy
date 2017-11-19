# -*- coding: utf-8 -*-
import re
import codecs
import os
import time

import lang
import kbay

import Sequencer as seq

SrcFileName='ieee_ALL'

def ieeePapers():
    print "load data from", SrcFileName
    with open('ieee/data/'+SrcFileName+'.txt', 'r') as f:
        for line in f:
            yield line

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

def refreshMemory2D(hist, steps):
    for w1, histOfW1 in hist.items():
        if hist[w1][w1] < steps * 0.001:
            hist.pop(w1)
    for w1 in hist:
        for w2, count in hist[w1].items():
            if count < hist[w1][w1] * 0.05:
                hist[w1].pop(w2)

def findPattern(DO_COOCUR=False, ROUND=1):

    for idx_raw, text in enumerate(ieeePapers()):
        idx = idx_raw + 1
        peek(idx, 1000)

        #if idx>10000: break

        ngram_local = {}
        sentences = lang.getSentenceList(text)

        for idofs, s in enumerate(sentences):

            tokenlist = lang.tokenize(s)

            seq.learnNewSequence(tokenlist)
            seq.blindMemorize(tokenlist)

            seq.showPatterns()
            pause()

findPattern()
