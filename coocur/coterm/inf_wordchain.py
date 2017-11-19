import cfg
import stat_counter as counter
import util as util
import fif as fif

def wordchain():
    print "find wordchain"
    terms = fif.load_json(cfg.FILE_TERM_DF_ABOVE2_JSON)
    chain_nex={} # this_word -> next_word -> count
    chain_pre={} # this_word -> previous_word -> count
    for t in terms:
        words = t.split()
        for i, w in enumerate(words[:-1]):
            counter.inc_2d(w, words[i+1], chain_nex)
            counter.inc_2d(words[i+1], w, chain_pre)
    print " - total term size", len(terms)
    print " - total nex_wordchain size", util.dictsize(chain_nex)
    print " - total pre_wordchain size", util.dictsize(chain_pre)

    for w in chain_nex.keys()[:5]: print w, "-->", chain_nex[w]
    for w in chain_pre.keys()[:5]: print w, "<--", chain_pre[w]
    while(1):
        w=raw_input('type type type')
        print ""
        print "   --> ",chain_nex[w]
        print "   <-- ",chain_pre[w]

if __name__=='__main__':
    wordchain()
