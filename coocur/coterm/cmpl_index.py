#
# Create INDEXes from TERMs to PAPERs
# Create INDEXes from WORDs to TERMs
#
import stat_counter as counter
import fif as fif
import util as util
import imp_pm_psr as psr

__IDX_TERM2PAPER_FILE ="pdb/pm_idx_t2p_ttl.json"
__IDX_WORD2TERM_FILE="pdb/pm_idx_w2t_ttl.json"

# MAKE following indexes (or mappings)
# 1. {TERM -> [paper id]} - TERM to PAPERS whose TITLE contains this TERM
# 2. {WORD -> [TERM]} - WORD to TERMS containing this WORD
def indexing():
    IndexT2P_InTtl={}
    IndexW2T_InTtl={}

    print "indexing using data from", psr.PM_TERM_FILE
    with open(psr.PM_TERM_FILE, 'r') as f:
        for line in f:
          pid, termTtl, termAbs, wordTtl, wordAbs = psr.parseTermLine(line)
          if not pid: continue
          for t in termTtl:
              if not t in IndexT2P_InTtl: IndexT2P_InTtl[t]=[]
              IndexT2P_InTtl[t].append(pid)

              for word in t.split():
                  counter.count_2d(word, [t], IndexW2T_InTtl)

        # save the indexes
        print "Size of Index TermTtl2Paper", util.dictsize(IndexT2P_InTtl)
        print "Size of Index Word2TermOfTtl", util.dictsize(IndexW2T_InTtl)
        fif.save_json(__IDX_TERM2PAPER_FILE, IndexT2P_InTtl)
        fif.save_json(__IDX_WORD2TERM_FILE, IndexW2T_InTtl)

# RETURN {index -> [paper id]}
def loadIndexT2P():
    return fif.load_json(__IDX_TERM2PAPER_FILE)
def loadIndexW2T():
    return fif.load_json(__IDX_WORD2TERM_FILE)

if __name__=='__main__':
    indexing()
