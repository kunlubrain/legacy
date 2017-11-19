#
# Calculate DOCUMENT FREQUENCY of TERMS/WORDS
#

import stat_counter as counter
import util as util
import fif as fif
import cfg

# FIND related terms by lexical similarity
def relatedTermByLexicon(TermJson, Word2TermJson, Save2Json):

    relatedTerms={} # TERM -> [related TERM]

    dfTermOfTtl = fif.load_json(TermJson)
    idxW2TTtl   = fif.load_json(Word2TermJson)
    print "find related terms"
    for t in dfTermOfTtl:
        words = t.split()
        wordSet = set(words)
        if not len(words)>1: continue
        # find other terms that also contain the same $words
        related = {}
        for w in words:
            containingTerms = idxW2TTtl.get(w,None)
            if not containingTerms: continue
            # this term must have a least two common words
            for ct in containingTerms:
                __nCommonWords=0
                for w2 in wordSet:
                    if w2 in ct: __nCommonWords+=1
                if __nCommonWords>=2: counter.inc(related, ct)
        if t in related: del related[t] # delete self relatedness
        top = sorted(related.items(), key=lambda (k,v):v, reverse=True)[:10]
        # sort again by DF
        top = [(k, dfTermOfTtl.get(k,0)) for (k,v) in top]
        top_s = sorted(top, key=lambda (k,v):v, reverse=True)[:5]
        rel = [i[0] for i in top_s]
        if not rel: continue
        #print "%s related to %s"%(t, top_s)
        relatedTerms[t]=rel
    fif.save_json(Save2Json, relatedTerms)

# FIND related terms by syntactical similarity
def relatedTermBySyntax():
    return

# FIND a map from WORD -> TERMs whoes first word is WORD
def headwording(TermJson, Save2Json):
    print "\nfind index from headword to terms"
    dfTermOfTtl = fif.load_json(TermJson)
    indexHeading_pre = {}
    indexHeading = {}
    for t, count in dfTermOfTtl.items():
        words = t.split()
        if not len(words)>1: continue
        headword = words[0]
        if not headword in indexHeading_pre:
            indexHeading_pre[headword]=[(t, count)]
    for hw, t in indexHeading_pre.items():
        indexHeading[hw] = sorted(t, key=lambda (term,count):count, reverse=True)

    fif.save_json(Save2Json, indexHeading)

if __name__=='__main__':
    rel.relatedTermByLexicon(TermJson=cfg.FILE_TERM_DF_TTL_JSON,
                             Word2TermJson=cfg.FILE_IDX_W2T_TTL_JSON,
                             Save2Json=cfg.FILE_TERM_REL_TTL_JSON)
    rel.relatedTermBySyntax()
    rel.headwording(TermJson=cfg.FILE_TERM_DF_ABOVE2_JSON,
                    Save2Json=cfg.FILE_TERM_HEAD_TTL_JSON)
