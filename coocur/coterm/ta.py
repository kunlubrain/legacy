# -*- coding: utf-8 -*-
#############################################
##              TEXT ANALYZER              ##
#############################################
import pubmed_nature_90 as PMED
import counter

## stream = s1, s2, s3, s4, ...
stream = "The foreign exchange market works through financial institutions, and it operates on several levels. Behind the scenes banks turn to a smaller number of financial firms known as “dealers,” who are actively involved in large quantities of foreign exchange trading. Most foreign exchange dealers are banks, so this behind-the-scenes market is sometimes called the “interbank market”, although a few insurance companies and other kinds of financial firms are involved. Trades between foreign exchange dealers can be very large, involving hundreds of millions of dollars. Because of the sovereignty issue when involving two currencies, forex has little (if any) supervisory entity regulating its actions."
stream = stream.split()
s1="transport of Itpr1 mRNA foo foo foo bar bar"
s2="components of RNA-transporting granules foo bar bar bar"
s3="thereby regulating its dendritic transport for synaptic"
#streams=[s1,s2,s3]
#streams=PMED.TITLES
NUM_PAPER = 3000
streams=PMED.ABSTRACTS[:NUM_PAPER]
streams=[s.lower().strip().replace(',','').replace('.','').split() for s in streams]

## n-th oder frequency classifier
## example 1st oder: "foo bar boo foo hii foo boo"
## gives:            foo:3, bar:1, boo:2, hii:1
def frqcls(stream, n, matrix_freq={}):
    print "\n##### %s-th oder freq classifier"%n
    last = len(stream) if n==1 else -(n-1)
    for i, s in enumerate(stream[:last]):
        if n==1:
            matrix_freq[s] = matrix_freq[s]+1 if s in matrix_freq else 1
            continue

        k = '_'.join(stream[i:i+n-1])
        nxt = stream[i+n-1]
        if not k in matrix_freq:
            matrix_freq[k] = {}
        matrix_freq[k][nxt] = matrix_freq[k][nxt]+1 if nxt in matrix_freq[k] else 1
    return matrix_freq

###################################################
###       POSTERIEOR PROBABILITY                ###
###################################################

def profilize(streams):
    '''profile each stream $return [{s1:n1, ..}, ..]'''
    series = []
    for s in streams:
        series.append(frqcls(s, 1, {}))
    return series

def prof(streams):
    '''profile all streams $return {s1:n1, ...}'''
    ### Interesting! It put everything in a mutatable
    ### matrix_freq if it is ommitted in the input arg
    for s in streams: x = frqcls(s, 1)
    return x

def post_profile(profiles, pp={}):
    '''$profiles: a set of profiles, each having structure
                  symbol -> occurence count
       $pp: posterior probability
       $return a $POST-PROFILE with structure
               symbol -> {symbol -> (cnt1, cntx)}, where
               cnt1: count x occurrence in one serie as 1
               cntx: count all x occurrences
       # posterior:
       #   Ns  Nr
       #    3   1    0.3
       #    2   0      0
       #    4   2    0.5
       # -> r's occurrence on s's occurrence     = 2 over 3
       # -> r's total number on s's total number = 3 over 9
    '''
    for prof in profiles:
        symbols = prof.keys()
        for s in symbols:
            for r in symbols:
                if not s in pp:    pp[s] = {}
                if not r in pp[s]: pp[s][r] = [0,0]

                nr = prof[r]
                pp[s][r][0] += 1  # cnt1
                pp[s][r][1] += nr # cntx
        print "*** pp %s symbols***\n"%len(pp)
    if 0:
        for x in pp:
            if pp[x][x][0]<5: continue
            for y in pp[x]:
                if pp[x][y][0]<5: continue
                print x, "  ",y, pp[x][y]
    return pp

def filter(pp):
    '''$pp is of $POST-PROFILE structure'''
    for s in pp:
        # profile of s as reference
        s_cnt1, s_cntx = float(pp[s][s][0]), float(pp[s][s][1])
        if s_cnt1 < 3: continue # not significant

        for r in pp[s]:
            r_cnt1, r_cntx = float(pp[s][r][0]), float(pp[s][r][1])

            prob_r_at_s = r_cntx/s_cntx


            rr_cnt1, rr_cntx = float(pp[r][r][0]), float(pp[r][r][1])
            rs_cnt1, rs_cntx = float(pp[r][s][0]), float(pp[r][s][1])

            prob_s_at_r = rs_cntx/rr_cntx

            if not (prob_r_at_s>0.5 and prob_s_at_r>0.5): continue
            if not (0.4 < prob_r_at_s/prob_s_at_r < 2.5): continue

            if s==r: continue
            print s, "->" ,pp[s][s], "[%s] -> "%r, pp[s][r]
            print r, "->" ,pp[r][r], "[%s] -> "%s, pp[r][s]
            print "    : p_r_at_s", prob_r_at_s
            print "    : p_s_at_s", prob_s_at_r

#==================================================

###################################################
###       TIME VARYING IMPORTANCE               ###
###################################################
tvif = [1, 0.98, 0.95, 0.9, 0.83, 0.71, 0.52, 0.21]
window_size = len(tvif)
def tvicls(stream, tvi={}):
    ### Time-Variant Importance indicator
    ## measures how adjacent two words are to appear
    ## left-importance  - appears to the left
    ## right-importance - appears to the right
    ##
    ## importance                     1 - 1 0.98 0.95 0.9 0.82
    ##
    ## time          ... -5 -4 -3 -2 -1 0 1    2    3   4    5 ........
    ##
    ## Time-Variant Importance Factors (centered)
    streamlen = len(stream)
    for i, s in enumerate(stream[:-1]):
        end = min(i+window_size+1, streamlen)
        if not s in tvi: tvi[s]={s:[0,0]} # init itself
        tvi[s][s][0] += 1 # this is its occurrence count
        tvi[s][s][1] += 1
        for j, r in enumerate(stream[i+1: end]):
            importance = tvif[j]
            if not r in tvi[s]: tvi[s][r]=[0,0]
            #tv[s][r] *= 0.8
            tvi[s][r][0] += 1 # counter
            tvi[s][r][1] += importance
#<==================================================

def selector(profile, minval=0):
    return [(p, profile[p]) for p in profile if profile[p]>minval]

def test_2ndoder():
    serie = {}
    for s in streams:
        frqcls(s, 2, serie)
    for k in serie: print k, " - ", selector(serie[k], 1)
    input()

for s in streams: p = frqcls(s, 4)
for w in p:
    #print '\n', w, '->', p[w]
    for nextw in p[w]:
        if p[w][nextw]>5:
            if 'cortex' in w+nextw:
                print w, nextw, '->', p[w][nextw]
input()

#profile = prof(streams)
#smean   = {}
#for s in profile: smean[s] = float(profile[s])/len(streams)
#if 0:
#    for k in smean:
#        if smean[k]>0.01: print k, smean[k]
#    input()


#profiles = profilize(streams)
#pprof = post_profile(profiles)
#filter(pprof)
#raw_input("pp done")

tvi={}
for s in streams:
    tvicls(s, tvi)
for s in tvi:
    if tvi[s][s][0] < 5: continue
    for r in tvi[s]:
        if tvi[s][r][0] < 2: continue
        print s, " -> ", r, tvi[s][r]

###############################################################
## Summary of What I Have
## - frequency classifier
##   [symbols] - occurrences
##      APPLICATION
##          - coocurrence in a chain
##
## - correlation
##   (symbol1, symbol2, correlation)
##
## - time varying importance
##   symbol -> [symbol1, symbol2, ...]
##      can predict the next symbol
##
## To Have
##   mark some important sentences
##      1. define the pattern of importance-indicator e.g. "we ... that" "our ... that"
##      2. collect a set of such sentences
##      3. profile this set and get key words pattern
##   classify a stream
##
