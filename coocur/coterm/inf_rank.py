#
# GIVEN
#       TERMS in TITLE
#       TERMS in ABSTRACT
#       FREQUENCY of WORDS in !this! ABSTRACT
#       FREQUENCY of TERMS in !this! ABSTRACT
#       DOCUMENT FREQUENCY of TERMS in TITLE
#       DOCUMENT FREQUENCY of TERMS in ABSTRACT
#       DOCUMENT FREQUENCY of WORDS in TITLE
#       DOCUMENT FREQUENCY of WORDS in ABSTRACT
#
# RANK
#       the SCORE(IMPORTANCE) of TERMS in ABSTRACT
#
# this_TERMs_TTL = TERMs in TTITLE
# for this_TERM in ABSTRACT
#   SCORE = 0
#   WORDs <- this_TERM
#   DFT_W = [DF_TITLE(this_WORD) for this_WORD in WORDs]
#   DFA_W = [DF_ABSTRACT(this_WORD) for this_WORD in WORD]
#
#   SCORE_DFT_W = DFT_W**2
#
#   if TERM_FREQUENCY > 1: score+1
#   if word in TITLE: score+1
#
#   specificity_term = DF_TERM_PUBMED / DF_TERM_REFDOMAIN
#
#   for w in words:
#       specificity_word = DF_WORD_PUBMED / DF_WORD_REFDOMAIN
#
#   CDF
#
#   - most unexpected: lowest df
#   - most relavant: common words to terms in title
#   - most likely: largest cdf
#   - most specificity: largest df_thisdomain/df_refdomain

import imp_pm_psr as imp
import cmpl_df as cmpl

def rank_t_abs():

    DFTAbs = cmpl.loadDFTermAbs()
    DFTTtl = cmpl.loadDFTermTtl()

    print "TERMs in ABSTRACT DF size=", len(DFTAbs)

    for p in imp.paperterms():
        pid = p[0]
        terms_abs = imp.getTermListAbs(p)
        terms_ttl = imp.getTermListTtl(p)
        ttl = ' '.join(terms_ttl)

        #score_df = sorted([(t, DFTAbs[t]) for t in terms_abs], key=lambda (t,n):n, reverse=True)
        #score_t = [1 for t in terms_abs if t in ttl]

        print "checking paper",pid
        for t in terms_ttl:
            print "  - title term: ",t.ljust(50), "DF", DFTTtl.get(t,0), "DF in ABS", DFTAbs.get(t,0)

        for t in terms_abs:
            w_ttl = 0
            for w in t.split():
                if w in ttl: w_ttl+=1
            print t.ljust(50), " DF %7s InTtl %s"%(DFTAbs.get(t,0), w_ttl)
        raw_input('gogo')

if __name__=='__main__':
    rank_t_abs()
