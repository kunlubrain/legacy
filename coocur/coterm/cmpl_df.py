#
# Calculate DOCUMENT FREQUENCY of TERMS/WORDS
#

import stat_counter as counter
import util as util
import fif as fif
import imp_pm_psr as psr

def df():

    DFTermTtl, DFTermAbs, DFWordTtl, DFWordAbs = {}, {}, {}, {}

    print "df calculation using data from",psr.PM_TERM_FILE
    with open(psr.PM_TERM_FILE, 'r') as f:
      for line in f:
        pid, termTtl, termAbs, wordTtl, wordAbs = psr.parseTermLine(line)
        counter.count(termTtl, DFTermTtl)
        counter.count(termAbs, DFTermAbs)
        counter.count(wordTtl, DFWordTtl)
        counter.count(wordAbs, DFWordAbs)

    print "Size of DF TermTtl", util.dictsize(DFTermTtl)
    print "Size of DF TermAbs", util.dictsize(DFTermAbs)
    print "Size of DF WordTtl", util.dictsize(DFWordTtl)
    print "Size of DF WordAbs", util.dictsize(DFWordAbs)
    fif.save_json("pdb/pm_df_t_ttl.json", DFTermTtl)
    fif.save_json("pdb/pm_df_t_abs.json", DFTermAbs)
    fif.save_json("pdb/pm_df_w_ttl.json", DFWordTtl)
    fif.save_json("pdb/pm_df_w_abs.json", DFWordAbs)

    DFTermTtl2 = util.dictfilter(DFTermTtl,2)
    DFTermAbs2 = util.dictfilter(DFTermAbs,2)
    DFWordTtl2 = util.dictfilter(DFWordTtl,2)
    DFWordAbs2 = util.dictfilter(DFWordAbs,2)
    print "Size of DF TermTtl above 2", util.dictsize(DFTermTtl2)
    print "Size of DF TermAbs above 2", util.dictsize(DFTermAbs2)
    print "Size of DF WordTtl above 2", util.dictsize(DFWordTtl2)
    print "Size of DF WordAbs above 2", util.dictsize(DFWordAbs2)
    fif.save_json("pdb/pm_df_t_ttl_2.json", DFTermTtl2)
    fif.save_json("pdb/pm_df_t_abs_2.json", DFTermAbs2)
    fif.save_json("pdb/pm_df_w_ttl_2.json", DFWordTtl2)
    fif.save_json("pdb/pm_df_w_abs_2.json", DFWordAbs2)


    DFTermTtl3 = util.dictfilter(DFTermTtl2,3)
    DFTermAbs3 = util.dictfilter(DFTermAbs2,3)
    DFWordTtl3 = util.dictfilter(DFWordTtl2,3)
    DFWordAbs3 = util.dictfilter(DFWordAbs2,3)
    print "Size of DF TermTtl above 3", util.dictsize(DFTermTtl3)
    print "Size of DF TermAbs above 3", util.dictsize(DFTermAbs3)
    print "Size of DF WordTtl above 3", util.dictsize(DFWordTtl3)
    print "Size of DF WordAbs above 3", util.dictsize(DFWordAbs3)
    fif.save_json("pdb/pm_df_t_ttl_3.json", DFTermTtl3)
    fif.save_json("pdb/pm_df_t_abs_3.json", DFTermAbs3)
    fif.save_json("pdb/pm_df_w_ttl_3.json", DFWordTtl3)
    fif.save_json("pdb/pm_df_w_abs_3.json", DFWordAbs3)

# return DF of TERMs in ABSTRACT
def loadDFTermAbs(): return fif.load_json("pdb/pm_df_t_abs_2.json")
def loadDFTermTtl(): return fif.load_json("pdb/pm_df_t_ttl_2.json")

if __name__=='__main__':
    df()
