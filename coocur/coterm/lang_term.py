import lang_checker as checker

import nltk
from nltk.tokenize import word_tokenize

def removeBadAnd(poslist):
    __adjtags  = ['JJ']
    newposlist=[]
    for i, pos in enumerate(poslist):
        # remove the 'and' after an adjective
        if pos[0]=='and':
            if not poslist[i-1][1] in __adjtags: continue
        newposlist.append(pos)
    return newposlist

''' returns a list of terms
'''
def termify(sentence):
    poslist_raw = nltk.pos_tag(word_tokenize(sentence))
    poslist = removeBadAnd(poslist_raw)

    _allowedTags = ['NN','JJ','NNS','NNP']
    def __goodword(w): return len(w)>1
    def __goodtag(t): return t in _allowedTags
    def __clean(p):
        return (p[0]+' ').replace('-','_') if __goodword(p[0]) and __goodtag(p[1]) else '#'

    terms = ''.join([ __clean(pos) for pos in poslist]).split('#')
    return [t.strip() for t in terms if t]

#########################
### term extraction
#########################

def filter_drop(sentence):
    #!F drop non useful word, ie. split by stop word
    return [ w for w in sentence.split() if checker.good(w) ]

def termify_naiive(sentence):
    #!F get a term list from the sentence by splitting on stop words
    #!P $sentence a list of words in the sentence
    def __clean(w):
        return (w+' ').replace('-','_') if checker.good(w) else '_._'

    terms = ''.join([ __clean(w) for w in sentence ]).split('_._')
    return [t.strip() for t in terms if t]


#########################
###  filters
#########################

def profiler_filter(terms, size=1):
    return [t for t, cnt in terms.items() if cnt>=size]

def pin_pos(wll, n_th):
    #!F pin by position: m[w] -> ['w a', 'w b', ...]
    # $wll word list list
    book = {} # map by the n_th word
    for wl in wll:
        w = wl[n_th]
        if not w in book: book[w] = [wl]
        else: book[w].append(wl)
    return book

def pin_headify(wll):
    return pin_pos(wll, n_th=0)

def pin_tailify(wll):
    return pin_pos(wll, n_th=-1)


# TODO
# - handle this case for 'and':
# ... development linking sensory and spinal gene regulatory programs.
#
# Two problems with following abstract:
#   - 'age of onset' instead of 'onset'
#   - 'mechanism linking ...' wrongly recognized as NN
#   - 'alter gene expression' the 'alter' is also recognized as a NN
#   - 'whereas' is considered NN, 'alters' as NN
#   - 'anterior' is considered as NN
# #'cis-regulatory variants that alter gene expression can modify disease expressivity, but none have previously been identified in huntington disease (hd)', 'here we provide in vivo evidence in hd patients that cis-regulatory variants in the htt promoter are bidirectional modifiers of hd age of onset', 'htt promoter analysis identified a nf-kappab binding site that regulates htt promoter transcriptional activity', 'a non-coding snp, rs13102260:g > a, in this binding site impaired nf-kappab binding and reduced htt transcriptional activity and htt protein expression', 'the presence of the rs13102260 minor (a) variant on the hd disease allele was associated with delayed age of onset in familial cases, whereas the presence of the rs13102260 (a) variant on the wild-type htt allele was associated with earlier age of onset in hd patients in an extreme case-based cohort', 'our findings suggest a previously unknown mechanism linking allele-specific effects of rs13102260 on htt expression to hd age of onset and have implications for htt silencing treatments that are currently in development']
#
# - Problem with nltk (it can not find the verb):
# - count these terms ['gaba controls critical_period plasticity', 'rat visual cortex']
#- 'sleep demonstrates'
