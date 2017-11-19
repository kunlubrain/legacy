# -*- coding: utf-8 -*-
import re
import codecs
import os
import time

import lang
import kbay
import klog

import fif

import memoryRefresh as mem

TEST_GRAMMER = 0
if TEST_GRAMMER:
    import grammer

Records   = {}
DFDir     = 'stats'
_SAVEDIR_ = 'ieee/stat/'

GRAM_DF = fif.readDFAsCountFromFile('ieee/stat/ieee_ALL_ngrams_total.txt', validation=0)

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

def ngramsOfSentence(s):

    tokenlist = lang.tokenize(s)
    if not len(tokenlist)>5:    return None
    if len(tokenlist)>80:       return None

    tokenstoplist = lang.markStops(tokenlist)
    poslist       = lang.posLookup(tokenlist)
    tokenVerbList = lang.markVerbs(tokenlist, poslist, verbose=False)
    tokenMarkList = lang.markStopOnNonending(tokenlist, poslist, tokenstoplist)
    tokenstoplist = lang.redoStops(tokenstoplist, tokenVerbList)
    tokenstoplist = lang.redoStops(tokenstoplist, tokenMarkList)
    ngb           = lang.ngrambounds(tokenstoplist)
    selecedngb    = lang.filterAdj(ngb, s)
    selecedngb    = lang.filterAdv(selecedngb, s)
    #selecedngb = lang.filterVerb(selecedngb, s, verbose=0) #<--- "contrast", "field" ignored
    selecedngb    = lang.filterSRS(selecedngb, tokenstoplist)

    return [t[0] for t in selecedngb]

def findNgrams(DO_COOCUR=False, ROUND=1):

    NGRAMS_DOC   = {}
    COOCUR_S     = {} # co-occurrence in a sentence
    NGRAM_LR     = {}

    for idx_raw, text in enumerate(ieeePapers()):
        idx = idx_raw + 1
        peek(idx, 1000)

        #if idx>10000: break

        ngram_local = {}
        sentences = lang.getSentenceList(text)

        for idofs, s in enumerate(sentences):

            tokenlist = lang.tokenize(s)
            poslist   = lang.posnize(tokenlist)

            if 0:
                print "\n-----tokens and poslist----"
                print ["(%s, %s)"%(t, poslist[i]) for i, t in enumerate(tokenlist)]

            if not len(tokenlist)>5:
                #print "Anormaly of sentence:", s, idofs
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
                    print "subject:", gram
                    #pause()

            if ROUND==2:
              try:
                # in the 2nd round, justify the gram
                for ngb in selecedngb:
                    sg = grammer.subgram(ngb[0], ngb[1], ngb[2], READIN_GRAM_LR, tokenlist, poslist)
                    if sg:
                      print "gram", ngb, "subgram", sg
                      raw_input()
              except:
                  pass

            if 1:
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

    kbay.saveHist3D(NGRAM_LR, _SAVEDIR_+'tmpnextword.txt')

    #print "filter df-doc"
    #filterHistByCount(NGRAMS_DOC, 2, verbose=False)
    #kbay.saveDF(NGRAMS_DOC,   _SAVEDIR_+SrcFileName+'_ngrams_df_doc.txt', sort=False, numDoc=idx)

    if DO_COOCUR:
      print "filter coocur"
      kbay.filterByCount2D(COOCUR_S, 2, verbose=True)
      kbay.saveDF2D(COOCUR_S, _SAVEDIR_+SrcFileName+'_ngrams_coocur.txt')

    print "DONE findNgrams"

def findDFOfWords():
    DF = {}
    for nFiles, text in enumerate(ieeePapers()):
        sentences = lang.getSentenceList(text)
        words = set(sum([wordlist(s, regular=True) for s in sentences], []))
        for w in words: DF[w] = DF.get(w, 0) + 1
        if nFiles%1000==0: print "finished",nFiles,"files"
    print "finished total",nFiles,"files"
    kbay.saveDF(DF, _SAVEDIR_+SrcFileName+'_df.txt', sort=False, numDoc=idx)

def linguisticScore(gram, leftindex, rightindex, tokenlist):

    score = 0

    if leftindex==0:
        score += 1

    if leftindex>0:
        lefttoken = tokenlist[leftindex-1]
        if lang.isGeneralDeterminor(lefttoken):
            score += 1

    if rightindex==len(tokenlist):
        score += 0.5

    if rightindex<(len(tokenlist)-1):
        righttoken = tokenlist[rightindex+1]
        if lang.isPuncturation(righttoken):
            score += 0.5
        if lang.isAuxVerb(righttoken):
            score += 1

    return score

# try to rank on the inverse DF
def selectTest():
    print "select test ..."
    book = fif.readWithFilter('ieeeGramDF_above3.txt', filtervalue=4)
    print "book size:", len(book)

    for idx_raw, text in enumerate(ieeePapers()):
        print text
        sentences = lang.getSentenceList(text)
        localHist = {}
        scoreByLang = {}
        gramLeftRight = {}
        for idofs, s in enumerate(sentences):
            tokenlist     = lang.tokenize(s)
            poslist       = lang.posLookup(tokenlist)
            tokenstoplist = lang.markStops(tokenlist)
            tokenVerbList = lang.markVerbs(tokenlist, poslist, verbose=False)
            tokenMarkList = lang.markStopOnNonending(tokenlist, poslist, tokenstoplist)
            tokenstoplist = lang.redoStops(tokenstoplist, tokenVerbList)
            tokenstoplist = lang.redoStops(tokenstoplist, tokenMarkList)
            ngb           = lang.ngrambounds(tokenstoplist)
            selecedngb    = lang.filterAdj(ngb, s)
            selecedngb    = lang.filterAdv(selecedngb, s)
            selecedngb    = lang.filterSRS(selecedngb, tokenstoplist)
            for g, l, r in selecedngb:
                localHist[g] = localHist.get(g, 0) + 1

                scoreByLang[g] = scoreByLang.get(g,0) + linguisticScore(g, l, r, tokenlist)
                if not g in gramLeftRight:
                    gramLeftRight[g] = []
                lefttoken  = '<L>' + ('#BEGIN' if l==0 else tokenlist[l-1])
                righttoken = '<R>' + ('#END' if r>=(len(tokenlist)-1) else tokenlist[r+1])
                gramLeftRight[g].append((lefttoken, righttoken))

        # scores
        scoreByDF = {}

        totalDF = 0
        for g in localHist:
            scoreByDF[g] = book.get(g, 0)
            totalDF = scoreByDF[g]
        averageDF = totalDF/len(scoreByDF)
        sortedByDF = sorted(scoreByDF.items(), key=lambda x:x[1], reverse=True)
        print sortedByDF
        print "average DF", averageDF
        print "gram with DF above average"
        print [(g, count) for (g, count) in sortedByDF if count>averageDF]
        print "gram with DF below average"
        print [(g, count) for (g, count) in sortedByDF if not count>averageDF]

        print "lang score:"
        print scoreByLang
        print "gram left right"
        print gramLeftRight 
        pause()

def findDFOfGrams():
    gramHist = {}
    for idx_raw, text in enumerate(ieeePapers()):
        localGramHist = {} # gram -> count
        sentences = lang.getSentenceList(text)
        for idofs, s in enumerate(sentences):
            tokenlist     = lang.tokenize(s)
            poslist       = lang.posLookup(tokenlist)
            tokenstoplist = lang.markStops(tokenlist)
            tokenVerbList = lang.markVerbs(tokenlist, poslist, verbose=False)
            tokenMarkList = lang.markStopOnNonending(tokenlist, poslist, tokenstoplist)
            tokenstoplist = lang.redoStops(tokenstoplist, tokenVerbList)
            tokenstoplist = lang.redoStops(tokenstoplist, tokenMarkList)
            ngb           = lang.ngrambounds(tokenstoplist)
            selecedngb    = lang.filterAdj(ngb, s)
            selecedngb    = lang.filterAdv(selecedngb, s)
            selecedngb    = lang.filterSRS(selecedngb, tokenstoplist)
            for g, l, r in selecedngb:
                localGramHist[g] = localGramHist.get(g, 0) + 1
                words= g.split()
                if len(words)>=3:
                    for ii, w in enumerate(words[:-1]):
                        posEndingWord = poslist[ii+1]
                        if "N" in posEndingWord or "X" in posEndingWord:
                            gg = " ".join(words[ii:ii+2])
                            localGramHist[gg] = localGramHist.get(gg, 0) + 1
                if len(words)>=4:
                    for ii, w in enumerate(words[:-2]):
                        posEndingWord = poslist[ii+2]
                        if "N" in posEndingWord or "X" in posEndingWord:
                            gg = " ".join(words[ii:ii+3])
                            localGramHist[gg] = localGramHist.get(gg, 0) + 1
                if len(words)>=5:
                    for ii, w in enumerate(words[:-3]):
                        posEndingWord = poslist[ii+3]
                        if "N" in posEndingWord or "X" in posEndingWord:
                            gg = " ".join(words[ii:ii+4])
                            localGramHist[gg] = localGramHist.get(gg, 0) + 1

        # save the local grams
        for g in localGramHist:
            gramHist[g] = gramHist.get(g, 0) + 1

        peek(idx_raw+1, 2000)

    kbay.saveDF(gramHist, 'ieeeGramDF.txt', sort=False, numDoc=idx_raw)

def filterGramDF():
    book = fif.readWithFilter('ieeeGramDF.txt', filtervalue=3)
    kbay.saveDF(book, 'ieeeGramDF_above3.txt', sort=False, numDoc=460035)

def testPos():
    for idx_raw, text in enumerate(ieeePapers()):
        sentences = lang.getSentenceList(text)
        for idofs, s in enumerate(sentences):
            tokenlist = lang.tokenize(s)
            tokenstoplist = lang.markRawPos(tokenlist)
            #lang.markVerbs(tokenlist)
            pause()

# Mutual information on GRAM by GRAMLIST given COOCUR
def relativeInfo(gram, gramlist, coocur):
    targetwords = gram.split()
    score = 0

    targetwordfreq = {}
    for w in targetwords:
        if w in coocur:
            targetwordfreq[w]=coocur[w][w]
        else:
            targetwordfreq[w]=1

    for g in gramlist:
        if g == gram: continue
        sourcewords = g.split()
        for sw in sourcewords:

            if not sw in coocur:
                continue

            swfreq = coocur[sw][sw]
            for tw in targetwords:
                twfreq = targetwordfreq[tw]
                cofreq = coocur[sw].get(tw, 1) # at least 1 time

                #if not cofreq>1:
                #    cofreq = 0.3*cofreq

                coscore = float(cofreq)/(swfreq*twfreq)
                score  += coscore
                print gram, tw, twfreq, sw, swfreq, cofreq, coscore
    return (gram, score)

def buildCoocurDemoNetwork():
    cobook = fif.readCoocurWithFilterFunc('tmp_ieee_coocur_abstractwide_grams.txt', None, filtervalue=2)
    selectedCobook = {}
    def __score(g):
        size = len(g.split())
        cnt  = hist[g]
        return size*size*cnt
    def __selectTop(pool, top, tel, gram, cobook, verbose=False):
        poolsize = len(pool)
        if poolsize>0:
            gramsize = len(pool[0].split())
            if gramsize==1:
                top = 3
            elif gramsize==2:
                top = 6 if poolsize*0.2<6 else int(poolsize*0.2)
                if top>10: top=10
            else:
                top = 5 if poolsize*0.5<5 else int(poolsize*0.5)
        else:
            top = 0

        topx = sorted([(g2, hist[g2]) for g2 in pool], key=lambda x:x[1], reverse=True)[:top]
        telx = sorted([(g2, hist[g2]) for g2 in pool], key=lambda x:x[1], reverse=True)[-tel:]
        if verbose:
            print "top", top, "from", len(pool)
            print topx
            print "tel", top, "from", len(pool)
            print telx
            #if raw_input('showdetails?')=='y': print pool
        for gg, cnt in topx:
            cobook[gram][gg] = cnt
    for g, hist in cobook.items():
        if not len(hist)>1: continue
        onegram, twogram, threegram, fourgram, xgram = [], [], [], [], []

        # make uniqukeys (deal with ambiguous terms, like XX, XXs, x y z, x Y, z)
        uniqkeys = set([])
        for k in hist.keys():
            alreadyIn = False
            for kk in uniqkeys:
                if len(k)> len(kk): minlen=len(kk)
                else: minlen = len(k)
                if k.lower()[:minlen-2]==kk.lower()[:minlen-2]:
                    alreadyIn = True
            if not alreadyIn:
                uniqkeys.add(k)

        for g2 in uniqkeys:
            if g2==g: continue
            size = len(g2.split())
            if   size==1: onegram.append(g2)
            elif size==2: twogram.append(g2)
            elif size==3: threegram.append(g2)
            elif size==4: fourgram.append(g2)
            else:         xgram.append(g2)

        #print "> ", g
        selectedCobook[g] = {}
        __selectTop(onegram,   3, 3, g, selectedCobook)
        __selectTop(twogram,   5, 5, g, selectedCobook)
        __selectTop(threegram, 5, 5, g, selectedCobook)
        __selectTop(fourgram,  5, 5, g, selectedCobook)
        __selectTop(xgram,     5, 5, g, selectedCobook)
        #print "> cobook:"
        #print selectedCobook
        #raw_input('...')
        # select maximu three 1-gram
        #averageCntOnegram = 1.0*sum([hist[g2] for g2 in onegram])/(len(onegram)
        #aboveAvrgOnegram  = [g2 for g2 in onegram if hist[g2] >= averageCntOnegram]
        #belowAvrgOnegram  = [g2 for g2 in onegram if hist[g2] < averageCntOnegram]

        #averageCnt = 1.0*sum([cnt for g2, cnt in hist.items() if g2!=g])/(len(hist)-1)
        #aboveAvrg = [(g2, cnt) for g2, cnt in hist.items() if cnt >= averageCnt]
        #topx = sorted(aboveAvrg, key=lambda x:x[1], reverse=True)[:10]
        #topx = sorted(hist.items(), key=lambda x:x[1], reverse=True)[:10]

        #selectedCobook[g] = {}
        #for (gg, c) in topx:
        #    if not gg==g:
        #        selectedCobook[g][gg] = c
    kbay.saveDF2D(selectedCobook, 'tmp_ieee_coocur_selected.txt')

def recommendTerms():
    dfbook = fif.readWithFilter('ieeeGramDF_above3.txt', filtervalue=4)
    cobook = fif.readCoocurWithFilterFunc('tmp_ieee_coocur_abstractwide_grams.txt', dfbook)
    for idx_raw, text in enumerate(ieeePapers()):
        sentences = lang.getSentenceList(text)
        coHist = {} # coocur_gram -> df for grams in abstract
        localHist = {} # local gram -> occurrence count
        for idofs, s in enumerate(sentences):
            grams = ngramsOfSentence(s)
            for g in grams:
                localHist[g] = localHist.get(g,0)+1
        for g in localHist:
            cograms = cobook.get(g, [])
            for gg in cograms:
                coHist[gg] = coHist.get(gg, [])
                coHist[gg].append(g)
        # just by mention/occurrence
        score = {}
        for g in localHist:
            cograms = cobook.get(g, [])
            if not g in cobook: continue
            gcount = cobook[g][g]
            for gg in cograms:
                if gg==g: continue
                cocount = cobook[g][gg]

                # ignore those with only one-degree of relavance for the moment
                if not len(coHist[gg])>1:
                    continue

                score[gg] = score.get(gg,0) + float(cocount)/gcount

        fluxAndPosterior = {}
        for g, colist in coHist.items():
            if not len(g.split())>1: continue
            if len(colist)>1:
                fluxAndPosterior[g] = (score[g], colist)

        print "grams of text:"
        print localHist.keys()

        print "cogram having influx > 2 ..."
        for g, colist in coHist.items():
            if len(colist)>1:
                print g, colist

        print "select from coHist ..."
        print sorted(coHist.items(), key=lambda x:len(x[1]), reverse=True)[:20]

        print "select from posterior..."
        print sorted(fluxAndPosterior.items(), key=lambda x:x[1][0])
        pause()

# Gi -> [Gj], where Gi is contained in Gj
# a Hessian Graph
def buildGramNetwork():
    dfbook = fif.readWithFilter('ieeeGramDF_above3.txt', filtervalue=5)
    vocab = {}
    groupedBySize = {}
    for g in dfbook:
        words = g.split()
        size  = len(words)
        if not size in groupedBySize:
            groupedBySize[size]=[]
        groupedBySize[size].append(g)
        for w in words: vocab[w]=1
    print "total vocab:", len(vocab)
    print "---size hist---"
    for s in groupedBySize:
        print "size=", s, "count=", len(groupedBySize[s])

    graph = {}
    for w in vocab: graph[w] = []

    def __findAllLeaves(word, verbose=False):
        frontierGrams = graph[word]
        leafnodes = []
        nIteration = 0
        while(frontierGrams):
            nextFrontier = []
            for g in frontierGrams:
                children = graph.get(g, None)
                if not children:
                    leafnodes.append(g)
                else:
                    nextFrontier += children
            frontierGrams = nextFrontier
            nIteration+=1
            if nIteration>10:
                print "too many iterations for:", word
                print "current frontier:", frontierGrams
                raw_input('...')
        if verbose:
            print "leafnodes for", word, " - ", leafnodes
        return leafnodes

    def __debugsize(size): return size>5000

    for size in sorted(groupedBySize.keys()):
        print "checking size=", size, "current graph size", len(graph)
        if size==1: continue
        for g in groupedBySize[size]:
            words = g.split()
            if __debugsize(size):
                print "\nchecking: ", g
            for w in words:
                leaves = __findAllLeaves(w, verbose=__debugsize(size))
                appendOnLeaf = False
                for l in leaves:
                    if l in g:
                        appendOnLeaf = True
                        if l==g:
                            # do not append to itself (already in graph)
                            continue
                        graph[l] = graph.get(l, [])
                        graph[l].append(g)
                        if __debugsize(size):
                            print "append: <", g,"> to:", l
                if not appendOnLeaf:
                    # append to this word
                    graph[w] = graph.get(w, [])
                    graph[w].append(g)
                    if __debugsize(size):
                        print "append: <", g,"> to:", w
            if __debugsize(size):
                raw_input()

    print "+++GRAPH+++"
    print "size:", len(graph)
    print "size(non-empty):", len([n for n in graph if graph[n]])
    #print graph
    g = raw_input('..')
    while g:
        if g=='look':
            print graph.keys()[:10]
            g = raw_input('..')
        else:
            if g in graph:
                print graph[g]
            else:
                print "not in graph"
            g = raw_input('..')

def memorizeCogram():

    book = fif.readWithFilter('ieeeGramDF_above3.txt', filtervalue=4)
    memo = mem.Memory()
    memo.setInitialCapacity(200)

    for idx_raw, text in enumerate(ieeePapers()):
        #if idx_raw<220000: continue
        sentences = lang.getSentenceList(text)
        gramsPreviousSentence = set([])
        for idofs, s in enumerate(sentences):
            grams = ngramsOfSentence(s)
            if not grams: continue
            goodgrams = set([g for g in grams if g in book])
            memo.learnSymbList(goodgrams)
            # grams of previous sentence: learn grams of current sentence
            # grams of current  sentence: learn grams of previous sentence
            memo.crosslearn(gramsPreviousSentence, goodgrams, crossweight=1)
            if 0 and len(list(gramsPreviousSentence)+list(goodgrams))==1:
                print "only 1 gram in two sentences!!!"
                print "sentence:", s
                print "grams before filtering:", grams
                print "grams after filtering", goodgrams
                if idofs>0:
                    print "previous sentence:", sentences[idofs-1]
                    print "previous grams before filtering:", ngramsOfSentence(sentences[idofs-1])
                    print "previous grams after filtering:", gramsPreviousSentence
                pause()
            gramsPreviousSentence = goodgrams

        peek(idx_raw+1, 2000)
        if (idx_raw+1)%2000==0:
            memo.refresh()
            memo.showsize()

        #if idx_raw>6000:
        #    break

    kbay.saveDF2D(memo.LTM, 'tmp_ieee_coocur_abstractwide_grams.txt')

def memorizeCoword():

    memo = mem.Memory()
    memo.setInitialCapacity(200)

    book = fif.readWithFilter('ieeeGramDF_above3.txt', filtervalue=4)

    for idx_raw, text in enumerate(ieeePapers()):
        #if idx_raw<70000: continue
        sentences = lang.getSentenceList(text)
        for idofs, s in enumerate(sentences):
            grams = ngramsOfSentence(s)
            if not grams: continue
            words = set(' '.join(grams).split())
            words = [w for w in words if w in book]
            memo.learnSymbList(words)

        peek(idx_raw+1, 2000)
        if (idx_raw+1)%2000==0:
            memo.refresh()
            memo.showsize()

    kbay.saveDF2D(memo.LTM, 'tmp_ieee_coocur_abstractwide_word_bymemo.txt')

def selectGrams():
    klog.msg('select grams')
    book=fif.readWordCoocur('tmp_ieee_coocur_abstractwide_words_4000.txt')
    #book=fif.readWordCoocur('tmp_ieee_coocur_abstractwide_word_bymemo.txt', filtervalue=2)
    CoHist = {}
    CoWord = {}
    klog.msg('looping files')
    for idx_raw, text in enumerate(ieeePapers()):
        localGramHist = {} # gram -> count
        sentences = lang.getSentenceList(text)
        for idofs, s in enumerate(sentences):
            tokenlist     = lang.tokenize(s)
            poslist       = lang.posLookup(tokenlist)
            tokenstoplist = lang.markStops(tokenlist)
            tokenVerbList = lang.markVerbs(tokenlist, poslist, verbose=False)
            tokenMarkList = lang.markStopOnNonending(tokenlist, poslist, tokenstoplist)
            tokenstoplist = lang.redoStops(tokenstoplist, tokenVerbList)
            tokenstoplist = lang.redoStops(tokenstoplist, tokenMarkList)
            ngb           = lang.ngrambounds(tokenstoplist)
            selecedngb    = lang.filterAdj(ngb, s)
            selecedngb    = lang.filterAdv(selecedngb, s)
            selecedngb    = lang.filterSRS(selecedngb, tokenstoplist)
            #print s
            #print "\n>INITIAL grams:\n", ngb
            #print "\n>SELECTED grams:\n", selecedngb
            for g, l, r in selecedngb:
                localGramHist[g] = localGramHist.get(g, 0) + 1

            if 0:
                print text
                print "#.localgrams:", len(localGramHist)
                print localGramHist
                print "#.ngram:", len([1 for g in localGramHist if ' ' in g])
                pause()

        #kbay.countCooccur(localGramHist, CoHist)

        # calculate mutual information
        gramlist = localGramHist.keys()
        gramscore = []
        for g in gramlist: gramscore.append(relativeInfo(g, gramlist, book))
        print sorted(gramscore, key=lambda x: x[1])
        averageScore = sum([g[1] for g in gramscore])/len(gramscore)
        print "above average:", averageScore
        print [g for g in gramscore if g[1]>averageScore]
        pause()

        wordset = set([w for g in localGramHist for w in g.split()])
        kbay.countCooccur(wordset, CoWord)

        peek(idx_raw+1, 1000)

        if (idx_raw+1)%4000==0:
            #mem.refreshMemory2D(CoWord, steps=idx_raw, prefilter=True)
            #h, hh = len(CoWord), kbay.sizeOf2DHist(CoWord)
            #print "hist size", h, hh, hh/h
            #mem.refreshMemory2DFirstOrder(CoWord, steps=idx_raw)
            kbay.saveDF2D(CoWord, 'tmp_ieee_coocur_abstractwide_words_%s.txt'%(idx_raw+1))
            CoWord={} # reset
            break

        if 0:
            if (idx_raw+1)%40000==0:
                kbay.saveDF2D(CoHist, 'tmp_ieee_coocur_abstractwide_%s.txt'%(idx_raw+1))
                CoHist={} # reset

    #kbay.filter2DHistByCount(CoWord, 3, verbose=True)
    #kbay.saveDF2D(CoWord, 'tmp_ieee_coocur_word.txt')

def findRelatedGrams():

    klog.msg('find co-exist terms')
    Hist = {}

    for idx_raw, text in enumerate(ieeePapers()):

        sentences = lang.getSentenceList(text)

        for idofs, s in enumerate(sentences):

            grams = ngramsOfSentence(s)
            kbay.countCooccurConsideringSubgram(grams, Hist, gramDF=GRAM_DF, debug=0)

        if idx_raw%1000==0:
            mem.refreshMemory2D(Hist, steps=idx_raw, prefilter=True)
            h, hh = len(Hist), kbay.sizeOf2DHist(Hist)
            print "hist size", h, hh, hh/h

        peek(idx_raw+1, 1000)
        if idx_raw>200000: break

    kbay.filter2DHistByCount(Hist, 2, verbose=True)
    kbay.saveDF2D(Hist, 'tmp_ieee_occur_all.txt')

#ieee_ALL.txt
#ieee_circ.txt
#ieee_electr.txt
#ieee_signal.txt
#ieee_bio.txt
#ieee_comput.txt
#ieee_info.txt
#ieee_wireless.txt

if TEST_GRAMMER:
    #READIN_GRAM_LR = kbay.readSavedHist3D('tmp.txt')
    READIN_GRAM_LR = kbay.readSavedHist3D(_SAVEDIR_+'tmpnextword.txt')
    print "gram PLR size=", len(READIN_GRAM_LR)

datafiles = os.listdir('ieee/data/')
datafiles = [d.split('.')[0] for d in datafiles]
for d in datafiles:
    if not re.search(r'ALL', d): continue

    SrcFileName = d

    # 1. df df of individual words (1-gram)
    #findDFOfWords()

    # 2. count of ngrams
    #findNgrams(DO_COOCUR=False, ROUND=1)

    #findRelatedGrams()
    #testPos()
    #selectGrams()
    #findDFOfGrams()
    #filterGramDF()
    #selectTest()
    #memorizeCoword()
    #memorizeCogram()
    #recommendTerms()
    #buildGramNetwork()
    buildCoocurDemoNetwork()

# NounPlural Verbing Prop =>
# "reliability of devices operating under DC voltages"
# ADJ + and + ADJ
# a strong economic and technical reason
# to + Verb + DET + NP
# keep "dispersion" while "removing other 1-gram", e.g. because dispersion appears more than one time in the abstract
# they believed that dispersion was important but gave no evidence for that assertion
# raw   ngb > [('believed', 1, 1), ('dispersion', 3, 3), ('gave', 7, 7), ('evidence', 9, 9), ('assertion', 12, 12)]
# how to determine the verb 'attenuate' in the following? 'of the NP VERB TO NON-VERB?'
# 'of the NP ADJ TO NON-VERB?'
# because the Fourier components of the pulse attenuate to insignificance before they can disperse to a degree that would cause appreciable change in the peak pulse amplitude or integral of the pulse waveform
# on the timing of the peak PD amplitude relative to other
#
# vice versa
# one purpose
# foo depends on
# V-N characteristics exhibited longer times to breakdown
