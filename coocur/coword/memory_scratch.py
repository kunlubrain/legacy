import kbay
import fif

#co = fif.readWordCoocur('stats/pmed/pmed_word_coocur.txt')
co = fif.readWordCoocur('stats/wiki_word_coocur.txt')

def infoscore(w1, w2):
    try:
        n_w1        = co[w1][w1]
        n_w2_on_w1  = co[w1].get(w2,0)
        n_w2        = co[w2][w2]
        n_total     = 2607000
    except:
        return 0

    r2    = float(n_w2)/n_total
    r2on1 = float(n_w2_on_w1)/n_w1
    score = r2on1 / r2
    return score

def sumscore(wordlist, wref):
    return sum([infoscore(w, wref) for w in wordlist])

if 0:
    for w1, hist in co.items():
        if not w1 in ['red', 'blue', 'black', 'green', 'orange', 'white', 'color']: continue
        print ">>> checking word", w1
        n_w1 = hist.get(w1)
        scores = []
        for w2, n_w2_on_w1 in hist.items():
            try:
                n_w2    = co[w2][w2]
            except:
                continue

            r1 = float(n_w2_on_w1)/n_w1
            r2 = float(n_w2_on_w1)/n_w2
            r2all = float(n_w2)/2607000
            #score = r1 * r2
            score = r2
            score = r2/r2all

            r1on2 = float(co[w2].get(w1,0))/n_w2
            r1all = float(n_w1)/2607000
            score1 = r1on2/r1all
            score2 = score

            score = score1*score2
            mutualEnforement = score1>1 and score2>1

            scores.append((w2, score, score1, score2, n_w2_on_w1, mutualEnforement))

        scores = sorted(scores, key=lambda x:x[1], reverse=True)
        #print scores
        selected = [s for s in scores if s[-1]]
        newscores = [(s[0], s[4]*s[3], s[4], s[3]) for s in selected]
        print sorted(newscores, key=lambda x:x[1], reverse=True)
        print "______________"
        print sorted(newscores, key=lambda x:x[2], reverse=True)
        raw_input('...')

    # total files
    totalFiles = 100000

    print "size of co-occur hist", kbay.sizeOf2DHist(co)

    for w1, hist in co.items():
        print ">>> checking word", w1
        n_w1 = hist.get(w1)
        selected = []
        candidates = []
        ncandidates = len(hist)
        evidenceStrenghth = []
        record = {}
        for w2, n_w2_on_w1 in hist.items():

            print "___ checking word", w2

            try:
                n_w2    = co[w2][w2]
            except:
                continue

            r_w2    = float(n_w2) / totalFiles
            r_w2_w1 = float(n_w2_on_w1) / n_w1
            i_w2_w1 = r_w2_w1/r_w2

            if not w1 in co[w2]:
                print "     ", w1, "discarded by", w2
                co[w1].pop(w2)
                continue

            candidates.append((w2, n_w2, n_w2_on_w1, r_w2, r_w2_w1, i_w2_w1))

            if w2!=w1:
                evidenceStrenghth.append((w2, float(n_w2_on_w1)/n_w2))
                record[w2]={}
                record[w2]['strength']=float(n_w2_on_w1)/n_w2
                record[w2]['info']=i_w2_w1
                record[w2]['n']=float(n_w2_on_w1)

            if not i_w2_w1>1:
                print "     ", w1, "noised by ", w2, "mutural info=", i_w2_w1
                co[w1].pop(w2)
                continue

            selected.append((w2, i_w2_w1))

            if 0:
                print "unconditional count of ", w1, n_w1
                print "unconditional count of ", w2, n_w2
                print "count of %s given %s:"%(w2, w1), n_w2_on_w1
                print "ratio of %s"%w2, r_w2
                print "ratio of %s given %s"%(w2, w1), r_w2_w1
                print "information of %s given %s "%(w2, w1), i_w2_w1
                raw_input()

        candidates = sorted(candidates, key=lambda x:x[-1], reverse=True)

        print "checking", w1, co[w1][w1]
        print ">>> candidate size", len(candidates)
        print ">>> preselection size ", ncandidates
        print ">>> selected size ", len(selected)
        print ">>> selected are: ", selected
        print ">>> candidates", candidates

        aveevi = sum([e[1] for e in evidenceStrenghth])/len(evidenceStrenghth)
        aveinf = sum([record[w]['info'] for w in record])/len(record)
        aven   = sum([record[w]['n'] for w in record])/len(record)

        for r in record:
            record[r]['inforatio']=record[r]['info']/aveinf
            record[r]['nratio']=record[r]['n']/aven

        print ">>> average strength", aveevi

        for e in evidenceStrenghth:
            record[e[0]]['strengthratio']=e[1]/aveevi

        for r, x in record.items():
            if r==w1: continue
            print "*%s/%s* %.4f"%(r, w1, aveinf)
            print "---<info, R>--- %.4f, %.4f"%(x['info'], x['inforatio'])
            print "---<evid, R>--- %.4f, %.4f"%(x['strength'], x['strengthratio'])
            print "---<n,    R>--- %5d, %.4f"%(x['n'], x['nratio'])
        raw_input()

    print "size of co-occur hist", kbay.sizeOf2DHist(co)

# Given the unconditional and conditional probabilities of the symbols, compute
# the kun-index of them
def kindex(s1, s2, CondHist, UncondHist):
    p_s1 = UncondHist[s1]
    p_s2 = UncondHist[s2]
    dist_s1 = CondHist[s1]
    dist_s2 = CondHist[s2]
    p_s1_on_s2 = dist_s2.get(s1, 0)/dist_s2['_']
    p_s2_on_s1 = dist_s1.get(s2, 0)/dist_s1['_']
    index = (p_s1_on_s2/dist_s1) * (p_s2_on_s1/dist_s2)

