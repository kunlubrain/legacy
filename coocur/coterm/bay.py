#!M bayersian profilers: get conditional distribution

def increment(symbol, profile):
    ''' A one-dimentional map from symbol to counter '''
    if not symbol in profile: profile[symbol]=0
    profile[symbol] += 1

def add2CD(s1, s2, p):
    #!F add to conditional distribution p(s2|s1):  p[s1][s2] -> count
    if not s1 in p:     p[s1]={}
    if not s2 in p[s1]: p[s1][s2]=0
    p[s1][s2] += 1

def count(symbollist, profile):
    #!F count each occurrence of symbol into the profile
    for s in symbollist:
        increment(s, profile)

def count_combine(d1, d2):
    #!F adding two profile into one, eg. {a:10},{a:2,b:1} => {a:12, b:1}
    #NOTE use Counter with Python2.7
    return dict( (k, d1.get(k,0)+d2.get(k,0)) for k in set(d1)|set(d2))

def count_show(profile, threshold=1):
    print "---"
    for k, cnt in profile.items():
        if cnt >= threshold:
            print "  - ", k, " : ", cnt

def count_filter(profile, threshold):
    return [k for k, cnt in profile.items() if cnt>=threshold]

def _typecheck(wl):
    assert type(wl)==type([]), "Expecting a list of words! Got: %s"%wl

def simpleProfile(wordlist, profile):
    for word in wordlist:
        increment(word, profile)

def dfProfile(docs, profile):
    #!F Document frequency gets #.documents containing each word
    #!P $docs: [[list of symbols for doc1], [list of symbols for doc2], ...]
    #!P $profile(word table): word -> count
    #
    #################################################
    # Document frequency
    #################################################
    # Given: a set of DOCUMENTs
    # Find:  a profile WORD ->  #.DOCUMENTs containing this word

    for symlist in docs:
        for word in set(symlist):
            increment(word, profile)

def rcd(wl, pm, lim=1, kw=None):
    #!F conditional distribution of previous words
    #!P $pm profile map
    #!P $kw key words that we focus on
    # Example:
    # w0 w1 w2 w3 w4 w5 w6 w7 w8 w9
    #             i
    # -----j-----
    # for w4, construct:
    # map[w4][w3]
    # map[w4][w2 w3]
    # map[w4][w1 w2 w3]
    # map[w4][w0 w1 w2 w3]
    _typecheck(wl)
    for i, s in enumerate(wl):
        if i==0: continue
        if kw and not s in kw: continue
        for j in range(lim+1)[1:]:
            begin = i-j
            if begin<0: break
            prefix_words = ' '.join(wl[begin:i])
            #print "add to cd: ", s, " --> ", prefix_words, "profile map:", pm
            add2CD(s, prefix_words, pm)

def lcd(wl, pm, lim=1, kw=None):
    #!F conditional distribution of following words
    _typecheck(wl)
    end_max = len(wl)
    for i, s in enumerate(wl[:-1]):
        if kw and not s in kw: continue
        for j in range(lim):
            end = i+j+2
            if end>end_max: break
            words = ' '.join(wl[i+1:end])
            add2CD(s, words, pm)

def simplelistcount(l, sort=True):
    # TODO replace with collection for python > 2.6
    #counted = dict([(i, l.count(i)) for i in l])
    #return sorted(counted.items(), key=lambda x: x[1])
    return dict([(i, l.count(i)) for i in l])

#given: [[s1, s2, s3], [s4, s5, s6], ...]
#find:  (si) -> count,  (si, sj) -> count, (si, sj, sp) -> count
def simplecounter(sentencelist):

    # 1 dimentional/item counter
    flatTermList = sum(sentencelist, [])
    flatWordList = sum([t.split() for t in flatTermList], [])
    wordcnt = simplelistcount(flatWordList)
    termcnt = simplelistcount(flatTermList)
    return wordcnt, termcnt

# operate on a list of list of hashables
# item -> count
# item -> frequency
def runningDF(coocurlist, condoccur):
    coocurlist = set(coocurlist)
    for s in (coocurlist):
        for r in (coocurlist):
            if s==r: continue
            add2CD(s, r, condoccur)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ideas in development ...
#
#
# left, right and middle
L_TRIMAP={}
R_TRIMAP={}
M_TRIMAP={}
def tripple(a, r, b, trimap):
    #!F find a relation like a-r-b
    #!F P(a,r|b) := m[b][a,r] -> count
    #!F P(r,b|a) := m[a][r,b] -> count
    key_sr = a+' '+r  # subject and relation
    key_ob = a+' '+b  # objects
    if not key_sr in trimap:
        trimap[key_sr] = {}
    if not b in trimap[key_sr]:
        trimap[key_sr][b] = 0
    trimap[key_sr][b] += 1

def __r1(su):
    #!F relation 1: a --> c --> b
    #!P seq := a sequence
    for i, a in enumerate(su[:-2]):
        r = su[i+1]
        b = su[i+2]
        if not usable(a): continue
        if not usable(r): continue
        if not usable(b): continue
        tripple(a, r, b, L_TRIMAP)
        tripple(a, b, r, M_TRIMAP)
