import math
import fif

def histsize(hist):
    return "%d : %d"%(len(hist), sum([len(kk) for k, kk in hist.items()]))

def forget_old(cohist, memcapacity, termfreq):
    # remove coocurred words with low mutual information
    # $memcapacity: max number of coocurred terms kept for a given term
    # $termfreq could be none

    print "> size before forget: ", histsize(cohist)

    def __score(cohist, w1, w2, termfreq, verbose=0):
        cocnt = cohist[w1][w2]
        if termfreq:
            w2cnt = termfreq[w2]
        else:
            w2cnt = cohist.get(w2, {}).get(w2, cocnt)
        #cocnt = math.sqrt(cocnt) if not w1 in cohist.get(w2,{}) else cocnt
        score = float(cocnt)/w2cnt
        if verbose:
            print ">", w1, w2
            print "cocnt", cocnt
            print "w2cnt", w2cnt
            print "score", score
        return score

    for w1 in cohist:

        if len(cohist[w1])<2: continue

        # select those above threshold
        scores = [(w2, __score(cohist, w1, w2, termfreq)) for w2 in cohist[w1].keys()]
        meanscore = (sum([s[1] for s in scores])-1)/(len(scores)-1) # -1 due to w1-w1
        selected = [s[0] for s in scores if s[1]>meanscore or s[1]>0.03]

        if len(selected)>memcapacity:
            scores = sorted(scores, key=lambda x:x[1], reverse=True)
            thresholdscore = scores[memcapacity-1][1]
            selected = [s[0] for s in scores if s[1]>thresholdscore]

        if w1=='red' and 0:
            scores = sorted(scores, key=lambda x:x[1], reverse=True)
            print "> scores", scores
            print "> meanscores", meanscore
            print "> selected:", selected
            raw_input()

        # remove those below threshold
        for w2, cnt in cohist[w1].items():
            if not w2 in selected:
                cohist[w1].pop(w2)

    print "> size after forget: ", histsize(cohist)
    return cohist

def __score(cohist, w1, w2, termfreq, verbose=0):
    cocnt = cohist[w1][w2]
    if termfreq: w2cnt = termfreq[w2]
    else: w2cnt = cohist.get(w2, {}).get(w2, cocnt)

    #cocnt = math.sqrt(cocnt) if not w1 in cohist.get(w2,{}) else cocnt
    score = float(cocnt)/w2cnt
    if verbose:
        print ">", w1, w2
        print "cocnt", cocnt
        print "w2cnt", w2cnt
        print "score", score
    return score

def select_by_capacity(w1, termfreq, cohist, memcapacity):

    selected = cohist[w1].keys()

    # those with coocurrence > 2
    candidates = [w2 for w2, cnt in cohist[w1].items() if cnt>1]
    singlet    = [w2 for w2, cnt in cohist[w1].items() if cnt==1]

    if len(candidates)>memcapacity:
        scores = [(w2, __score(cohist, w1, w2, termfreq)) for w2 in candidates]
        scores = sorted(scores, key=lambda x:x[1], reverse=True)
        thresholdscore = scores[memcapacity-1][1]
        selected = [s[0] for s in scores if s[1]>thresholdscore]
        return selected+singlet
    else:
        return selected

def select_by_average(w1, termfreq, cohist):
    # select those above threshold
    scores = [(w2, __score(cohist, w1, w2, termfreq)) for w2 in cohist[w1].keys()]
    meanscore = (sum([s[1] for s in scores])-1)/(len(scores)-1) # -1 due to w1-w1
    selected = [s[0] for s in scores if s[1]>meanscore]
    return selected

def forget(cohist, termfreq, forgetby, memcapacity=None):
    # remove coocurred words with low mutual information
    # $memcapacity: max number of coocurred terms kept for a given term
    # $termfreq could be none

    print "> size before forget: ", histsize(cohist)

    i=0
    for w1 in cohist:
        i+=1
        if(i%1e3==0): print "finished",i,"words"
        memsize = len(cohist[w1])
        if memsize<2: continue

        if forgetby=='capacity':
            if memsize < memcapacity: continue
            selected = select_by_capacity(w1, termfreq, cohist, memcapacity)
        elif forgetby=='average':
            selected = select_by_average(w1, termfreq, cohist)
        else:
            assert 0, 'bad forgetby: %s'%forgetby

        # remove those below threshold
        for w2, cnt in cohist[w1].items():
            if w1==w2: continue
            if not w2 in selected:
                cohist[w1].pop(w2)

    print "> size after forget: ", histsize(cohist)
    return cohist

def normalize(cohist):
    n = {}
    for w, h in cohist.items():
        if w in h:
            del cohist[w][w]
    for w, h in cohist.items():
        n[w] = {}
        total = sum([count for ww, count in h.items()])
        for ww, count in h.items():
            n[w][ww] = float(count)/total
    return n

def forgetOnFile(ctffile, memcapacity, save2file, normlized=True):
    cohist = fif.readWordCoocur(ctffile)
    cohist = forget(cohist, termfreq=None, forgetby='average', memcapacity=None)
    if normlized:
        h = normalize(cohist)
    else:
        h = cohist
    fif.saveHist2D(h, save2file, splitter=',')

forgetOnFile('stats/wiki_word_coocur.txt', 100, 'stats/wiki_word_coocur_filtered.csv')
forgetOnFile('stats/wiki_de_word_coocur.txt', 100, 'stats/wiki_de_word_coocur_filtered.csv')
