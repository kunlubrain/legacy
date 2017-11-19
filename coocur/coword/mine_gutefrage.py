# -*- coding: utf-8 -*-
import counter as counter
import re
import fif
import memory as mem
from histsize import histsize_3d, histsize_4d

# loop through the file
# file -> [sentence] => sentence -> [noun|ngram]
# construct:
# - tf
# - ctf2
# - ctf3

def read_gutefrage(fin, tf={}, debug=0):

    print "read and build tf from", fin

    with open(fin, 'r') as fh:
        for i, line in enumerate(fh):

            if debug==1:
                print " - check line %d:"%i, line

            if (i%1e3==0 and i>1): print "processed %d lines"%i, "len tf",len(tf)
            txt = re.sub('#', ' ', line.strip('\n'))
            counter.count_tf(tf, txt, by='sent', debug=debug)

    print "[DONE build tf] len tf=", len(tf)

    return tf

def do_ctf(fin, tf, refreshperiod, denoise_ratio, cutoff, ctf):
    with open(fin, 'r') as fh:
        for i, line in enumerate(fh):
            txt = re.sub('#', ' ', line.strip('\n'))
            counter.count_ctf(i, txt, tf, by='sent',
                              refresh_period=refreshperiod,
                              denoise_ratio=denoise_ratio,
                              ctf=ctf
                             )
            if i%2000==0 and i>1: print "<-- done %d lines\n"%i

    print "\n> final mem denoise and forget"
    mem.denoise_by_absolute(ctf, cutoff)
    for w, h in ctf.items():
        if len(h)<2:
            ctf.pop(w)
    mem.forget(ctf, termfreq=tf, forgetby='average')

    print "> do_ctf done: len ctf=", len(ctf)

def do_semantic(fin, ctf, refresh_period, ctf3={}):
    with open(fin, 'r') as fh:
        for i, line in enumerate(fh):
            txt = re.sub('#', ' ', line.strip('\n'))
            counter.count_ctf3(txt, by='sent', significants=ctf, ctf3=ctf3)

            if i%refresh_period==0 and i>1:
                print "i=", i, "ctf size=", histsize_3d(ctf3)

    # final: remvoe all noise
    print "final: remove noises"
    for t, h in ctf3.items():
        for tt, hh in h.items():
            for ttt, hhh in hh.items():
                if hhh<2:
                    ctf3[t][tt].pop(ttt)
    return ctf3


FIN = 'content_gutefrage.txt'
TF = {}
CTF = {}
FOUT_TF = 'stats/gutefrage/tf_gutefrage.txt'
FOUT_TF = 'stats/gutefrage/tf_gutefrage_ng.txt'
FOUT_CTF = 'stats/gutefrage/ctf_gutefrage.txt'
FOUT_CTF = 'stats/gutefrage/ctf_gutefrage_ng.txt'
FOUT_CTF3 = 'stats/gutefrage/ctf3_gutefrage.txt'

if 0:
    #TODO - a way to register the nbatch
    read_gutefrage(FIN, TF, debug=0)
    raw_input('-----')

    fif.saveTF(TF, totalWordCount=1, fname=FOUT_TF)

raw_input('--- tf done ---')

if 1:
    print "\n --- coocur ctf ---"
    tf = fif.readTF(FOUT_TF, {}, threshold=5)
    print "selected tf size", len(tf)
    raw_input('-----')
    do_ctf(FIN, tf, refreshperiod=2*1e4, denoise_ratio=0.0019, cutoff=2, ctf=CTF)
    fif.saveHist2D(CTF, FOUT_CTF)
raw_input('--- ctf done ---')

if 1:
    print "\n --- semantic ---"
    ctf = fif.readWordCoocur(FOUT_CTF, 1)
    print "> initial ctf size", mem.histsize(ctf)
    ctf3 = do_semantic(FIN, ctf, refresh_period=1e4, ctf3={})
    print "> final size", histsize_3d(ctf3)
    fif.saveHist3D(ctf3, FOUT_CTF3)
