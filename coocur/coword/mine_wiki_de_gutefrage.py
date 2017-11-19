# -*- coding: utf-8 -*-
import re
import kutils
import codecs
import os
import time

import lang_cleaner as cleaner
import mine_helper_fif
import klog
import kbay
import fif
import pattens as pt
import nlp_de_stops as nlp
import coocur as mem
from histsize import histsize_3d, histsize_4d


def pause(): raw_input('pause...')

def loopWikiData():
    datafiles = os.listdir('data_wiki_de')
    nFiles = 0
    for datafile in datafiles:
        nFiles += 1
        if(nFiles%1000==0): print "[DONE] %d files"%nFiles
        fname = 'data_wiki_de/' + datafile
        with open(fname, 'r') as fh:
            text =  fh.read()
            yield datafile, text, nFiles

def sentences():
    # serialize a sequence of sentence

    for idx, (datafile, text, nfiles) in enumerate(loopWikiData()):
        sentences = cleaner.getSentences(text)
        for s in sentences:
            yield s

def termsOfBatch(grammode='uni'):
    # terms: default to uni-gram
    # batch: size of a text unit or block to analyse, default to sentence

    for s in sentences():
        if grammode=='uni':
            yield sent2Unigram(s)
        elif grammode=='ng':
            yield sent2Unigram_de(s)
        elif grammode=='uni_allwords':
            yield sent2Unigram_de_allwords(s)
        else:
            assert 0, "bad gram mode %s"%mode
        #raw_input()

def sent2Unigram_de_allwords(s):
    ss = re.sub('[:,%\"\']', ' ', s)
    words = ss.split()
    ss = ' '.join(['' if w.lower() in nlp.stopwords() else w for w in words])
    grams = ss.split()
    gs = []
    for g in grams:
        if len(g)<2: continue
        if not re.match('^\w+$', g, re.UNICODE): continue
        if re.search('[0-9]', g): continue
        gs.append(g)
    #grams = [g for g in grams if len(g)>1 and (not re.match('^\w+$', g, re.UNICODE)) and not re.search('[0-9]', g)]
    return set(gs)

def sent2Unigram_de(s):
    # split on german stopwords
    ss = re.sub('[:,%\"\']', ' ', s)
    words = ss.split()
    ss = ' '.join(['#' if w.lower() in nlp.stopwords() else w for w in words])
    ss = re.sub('#[#\s]+', '#', ss)

    ngrams = [i.strip() for i in ss.split('#')]

    # cleaning
    def __check(ng):
        if re.search('[0-9]', ng): return '' # ignore digits
        if len(ng)<3: return ''
        if not re.match('^[\w\s]+$', ng, re.UNICODE):
            return ''
        ng = ' '.join(['' if w.lower() in nlp.stopwords() else w for w in ng.split()])
        return ng

    ngrams = [g for g in [__check(ng) for ng in ngrams] if g]

    return set(ngrams)

def sent2Unigram(s):
    grams = [g for g in re.findall(pt.GERMAN_NOUN_UNI, s) if not g.lower() in nlp.stopwords()]
    return set(grams)

def tfOfBatch(samplesize, grammode, tf={}):
    # build Term-Frequency from batches

    for nbatch, terms in enumerate(termsOfBatch(grammode)):
        if nbatch>samplesize: break
        for t in terms:
            tf[t] = tf.get(t,0) + 1
        if nbatch%(size_mem_refresh)==0 and nbatch>1e3:
            print "> tf size", len(tf), "nbatch=", nbatch
            if nbatch>size_mem_terminate: break
    return tf, nbatch

def clean_ctf_absolute(ctf, threshold):
    print "> [remove noise] before", mem.histsize(ctf)
    for w1, hist in ctf.items():
        for w2, cnt in hist.items():
            if not cnt>threshold:
                ctf[w1].pop(w2)
    print "> [remove noise] after", mem.histsize(ctf)

def clean_ctf_relevant(ctf, threshold):
    print "  > [remove noise] before", mem.histsize(ctf)
    for w1, hist in ctf.items():
        self_cnt = hist[w1]
        for w2, cnt in hist.items():
            if not cnt > self_cnt * threshold:
                ctf[w1].pop(w2)
    print "  > [remove noise] after", mem.histsize(ctf)

def ctfOfBatch(samplesize, selectedterms, grammode, denoise_ratio, ctf={}):
    # $selectedterms: only builld ctf for those

    for nbatch, terms in enumerate(termsOfBatch(grammode)):
        if nbatch>samplesize: break

        #if nbatch%(20*4000)==0:
        #    memory.refresh(ctf, steps=nbatch, verbose=0)

        # select only those worth attention
        terms = [t for t in terms if t in selectedterms]
        kbay.countCooccur(terms, ctf)

        # refresh memory
        if nbatch%(size_mem_refresh)==0 and nbatch>1e3:

            print "ctf size=", len(ctf), "nbatch=", nbatch
            mem.forget(ctf, termfreq=selectedterms, forgetby='capacity', memcapacity=100)

            # remove noise early
            if nbatch%(size_mem_denoise)==0:
                clean_ctf_relevant(ctf, denoise_ratio) # 0.003)

            # termination
            #if len(ctf)>100200: break
            if nbatch>size_mem_terminate: break

    clean_ctf_absolute(ctf, 2)

    print "> final mem refresh, nbatch=", nbatch
    mem.forget(ctf, termfreq=selectedterms, forgetby='average')

    return ctf, nbatch

def semantic(significants, grammode, ctf3={}):
    # $significants: a 2d dict of those related terms
    #

    for nbatch, terms in enumerate(termsOfBatch(grammode)):
        for t in terms:
            if not t in significants: continue
            if not t in ctf3: ctf3[t]={}
            related = significants[t]
            for tt in terms:
                if tt==t: continue
                if not tt in related: continue
                if not tt in ctf3[t]: ctf3[t][tt]={}
                # a magic self-counter
                #ctf3[t][tt]['#'] = ctf3[t][tt].get('#', 0) + 1
                for ttt in terms:
                    if ttt==t or ttt==tt: continue
                    if not re.search('[a-zäöü]', ttt[0]): continue
                    ctf3[t][tt][ttt] = ctf3[t][tt].get(ttt, 0) + 1

        if nbatch%(size_mem_refresh)==0 and nbatch>1e3:
            print "nbatch=", nbatch, "ctf size=", histsize_3d(ctf3)
            #mem.forget3d(ctf3, forgetby='capacity', memcapacity=100)

            if nbatch>size_mem_terminate: break

    # final: remvoe all noise
    print "final: remove noises"
    for t, h in ctf3.items():
        for tt, hh in h.items():
            for ttt, hhh in hh.items():
                if hhh<3:
                    ctf3[t][tt].pop(ttt)
    return ctf3

# config
SAMPLE_SIZE = 1e7
fname_tf = 'stats/gutefrage/tf.txt'
fname_tf_top = 'stats/gutefrage/tf_top.txt'
FOUT_TF = 'stats/gutefrage/tf_ng.txt'
FOUT_TF_TOP = 'stats/gutefrage/tf_ng_top.txt'
fname_ctf = 'stats/gutefrage/ctf.txt'
fname_ctf = 'stats/gutefrage/ctf_inplace_cap100.txt'
fname_ctf = 'stats/gutefrage/ctf_inplace_cap100_earlydenoise.txt'
fname_ctf = 'stats/gutefrage/ctf_above2.txt'
fname_ctf = 'stats/gutefrage/ctf_above5.txt'
FOUT_CTF = 'stats/gutefrage/ctf_ng.txt'
fname_ctf_mem = 'stats/gutefrage/ctf_mem_above5.txt' # only the memorized
fname_ctf_mem = 'stats/gutefrage/ctf_mem.txt' # only the memorized
fname_semet3 = 'stats/gutefrage/ctf_mem_sem3.txt'
fname_semet3 = 'stats/gutefrage/ctf_mem_allwords_sem3.txt'
fname_semet4 = 'stats/gutefrage/ctf_mem_sem4.txt'

size_mem_refresh = 1*1e5
size_mem_denoise = 2*1e5
size_mem_terminate = 70*3*1e4

size_mem_refresh = 2*1e5
size_mem_terminate = 20*1e5

size_mem_refresh = 1*1e3
size_mem_terminate = 5*1e3

size_mem_refresh = 2*1e5
size_mem_terminate = 10*1e5

TEST_TF, TEST_CTF, TEST_MEMORY, RUN_SEMANTIC = 0, 0, 0, 1
GRAM_MODE = 'uni_allwords'

if TEST_TF:
    # to config:
    # GRAM_MODE, SAMPLE_SIZE, FOUT_TF

    # build tf
    tf, nbatch = tfOfBatch(SAMPLE_SIZE, grammode=GRAM_MODE)

    # save the 1D tf
    fif.saveTF(tf, nbatch, FOUT_TF)

    # select only the top x
    avefreq = sum([c for t,c in tf.items()])/len(tf)
    selectedterms = dict([(t,c) for t,c in tf.items() if c>avefreq])
    for t,c in tf.items():
        if not c>28:
            tf.pop(t)
    fif.saveTF(tf, SAMPLE_SIZE, FOUT_TF_TOP)

if TEST_CTF:
    print "read term frequncy"
    # read term-frequency and select those worth attention
    tf = fif.readTF(FOUT_TF_TOP)

    print "build conditional-tf"
    # build conditional-tf
    ctf, nbatch = ctfOfBatch(SAMPLE_SIZE, tf, grammode='ng', denoise_ratio=0.003)

    # save the 2D conditional tf
    fif.saveHist2D(ctf, FOUT_CTF)

if TEST_MEMORY:
    mem.forgetOnFile(ctffile=fname_ctf, memcapacity=100, save2file=fname_ctf_mem)
    # it does not finish
    # size before forget: 100201 : 34424319
    # ==> filter when reading the file!!!

if RUN_SEMANTIC:
    ctf = fif.readWordCoocur(fname_ctf_mem, 10)
    print "> initial ctf size", mem.histsize(ctf)
    ctf3 = semantic(ctf, grammode=GRAM_MODE, ctf3={})
    print "> final size", histsize_3d(ctf3)
    fif.saveHist3D(ctf3, fname_semet3)

def semantic4(significants, ctf={}):

    for nbatch, terms in enumerate(termsOfBatch()):
        for t in terms:
            if not t in significants: continue
            related = significants[t]
            for tt in terms:
                if tt==t: continue
                if not tt in related: continue
                related2 = significants[t][tt]
                for ttt in terms:
                    if ttt==t or ttt==tt: continue
                    if not ttt in related2: continue

                    for tttt in terms:
                        if tttt==t or tttt==tt or tttt==ttt: continue
                        if not t in ctf: ctf[t]={}
                        if not tt in ctf[t]: ctf[t][tt]={}
                        if not ttt in ctf[t][tt]: ctf[t][tt][ttt]={}
                        ctf[t][tt][ttt][tttt] = ctf[t][tt][ttt].get(tttt, 0) + 1

        if nbatch%(size_mem_refresh)==0 and nbatch>1e3:
            print "nbatch=", nbatch, "ctf size=", histsize_4d(ctf)
            if nbatch>size_mem_terminate: break

    # final: remvoe all noise
    print "final: remove noises"
    for t, h in ctf.items():
        for tt, hh in h.items():
            for ttt, hhh in hh.items():
                for tttt, hhhh in hhh.items():
                    if hhhh<3:
                        ctf[t][tt][ttt].pop(tttt)
    return ctf

RUN_SEMANTIC4 = 0
if RUN_SEMANTIC4:
    ctf = fif.readCTF3(fname_semet3, 10)
    ctf4 = semantic4(ctf, ctf={})
    fif.saveHist4D(ctf4, fname_semet4)

#...
# [DONE] 65000 files
# ctf size= 56291 nbatch= 2150000
# > size before forget:  56291 : 16431517
# > size after forget:  56291 : 16260232
# > [remove noise] before 56291 : 16260232
# > [remove noise] after 56291 : 1700171
# > final mem refresh, nbatch= 2150000
# > size before forget:  56291 : 1700171
# > size after forget:  56291 : 642695
# [DONE] Saved to stats/gutefrage/ctf_inplace_cap100_earlydenoise.txt len= 56291













# TODO - german stopword list
# TODO - handle the first word of sentence
# TODO - put the regex patterns into one file
# TODO - get sentences
