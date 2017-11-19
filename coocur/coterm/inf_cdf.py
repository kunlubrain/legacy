#
# Calculate DOCUMENT FREQUENCY of TERMS/WORDS
#

import stat_counter as counter
import util as util
import fif as fif
import imp_pm_psr as impt
import cmpl_index as cmpl

FILE_CDF_TTL2TTL_JSON='pdb/pm_cdf_ttl2ttl.json'
FILE_CDF_TTL2ABS_JSON='pdb/pm_cdf_ttl2abs.json'

# GIVEN: term -> [paper id]
#        paper id -> [terms]
# FIND:  conditional df {term -> {term -> count}}
# PARA:  only consider terms that occur in more than $threshold_ppr papers
#        only consider cooccured terms that cooccured more than $threshold_occ times
#        set $threshold_ppr=0 will keep all terms
# NOTE:  the calculation here is similar to a SQL-statement
def cdf(term_getter, jsonfile, threshold_ppr=0, threshold_occ=2, debug=0):

    print "find cdf: using term getter",term_getter,"ppr>",threshold_ppr,"coocr>",threshold_occ
    _conditionalDF = {}
    mapT2P = cmpl.loadIndexT2P()
    # TODO - load only the ">2" terms
    mapP2T = impt.loadP2T(term_getter)

    print "find cdf: loop all terms"
    # for each term check all papers whose title containing this term
    for t in mapT2P:
        if not t: continue
        if not len(t.split())>1: continue
        pidlist = mapT2P[t]
        if not len(pidlist)>threshold_ppr: continue

        # for each paper, count the terms based on $term_getter
        for pid in pidlist:
            targetTerms = [i for i in mapP2T[pid] if len(i.split())>1]

            counter.count_2d(t, targetTerms, _conditionalDF)
            #print t, " in:", pid, "co-terms:", targetTerms

        #delete terms that do not co-occur more than $threshold times
        util.dictfilter2d_inplace(_conditionalDF, threshold_occ)

        #if(len(_conditionalDF)>10): break

    util.dictfilter2d_nonempty_inplace(_conditionalDF)

    for k in _conditionalDF.keys()[:10]:
        print "Conditional DF - %s => %s"%(k,_conditionalDF[k])
    print "Conditional DF: %s"%util.dictsize(_conditionalDF)

    fif.save_json(jsonfile, _conditionalDF)

# FIND CDF of TERMS in TITLE given a TERM in TITLE
def cdf_ttl2ttl():
    cdf("ttl", FILE_CDF_TTL2TTL_JSON, threshold_ppr=10, threshold_occ=2)

# FIND CDF of TERMS in ABSTRACT given a TERM in TITLE
def cdf_ttl2abs():
    cdf("abs", FILE_CDF_TTL2ABS_JSON, threshold_ppr=10, threshold_occ=3)

if __name__=='__main__':
    cdf_ttl2ttl()
    cdf_ttl2abs()
