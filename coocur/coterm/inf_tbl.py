# generate a few tables at inference stage using previously mined results
import imp_pm_psr as imp
import imp_pm_readin as readin
import fif as fif

# generate table:
# paper_id, terms_ttl, terms_abs
def genTblPaperTerm(TermTbl):
    print "generate paper->term table"

    FILE_PT_CSV = 'pdb/SqlPaperTerm.csv'
    fif.resetFile(FILE_PT_CSV)

    sig_t_abs = fif.load_json('pdb/pm_df_t_abs_3.json')

    print "dump records to", FILE_PT_CSV
    for pt in readin.paperterms():
        pid, t_ttl, t_abs = pt[0], pt[1], pt[2]

        # remove some terms of abstract
        t_abs_good = [t for t in t_abs if sig_t_abs.get(t,0)>5 and sig_t_abs[t]<2000]

        # rank the 1gram by df (lower is better)
        t_abs_ngram = [t for t in t_abs_good if len(t.split())>1]
        t_abs_1gram = [t for t in t_abs_good if not t in t_abs_ngram]
        t_abs_1gram = sorted(t_abs_1gram, key=lambda k: sig_t_abs[k])[:2]

        #TODO: better to check abbreviation, if offen in title or frequent terms, etc

        def __termCount(term):
            return '%s:%s'%(term, TermTbl.get(term, 0))

        ttl_term_str = ';'.join([__termCount(t) for t in t_ttl])
        abs_term_str = ';'.join([__termCount(t) for t in t_abs_ngram+t_abs_1gram])

        line = '%s,%s,%s'%(pid, ttl_term_str, abs_term_str)
        fif.addLineToFile(FILE_PT_CSV,line)

def genRelTermTbl_lex(TermTbl):
    rel_lex = fif.load_json('pdb/pm_rel_t_ttl.json')
    FILE_REL_LEX_CSV='pdb/pm_relatedterms_lexical.csv'
    fif.resetFile(FILE_REL_LEX_CSV)
    for ref_term, terms in rel_lex.items():
        if TermTbl.get(ref_term,0)==0: continue
        term_str = '|'.join(['%s;%s'%(t,TermTbl.get(t,0)) for t in terms])
        line = '%s,%d,%s'%(ref_term,TermTbl.get(ref_term,0),term_str)
        fif.addLineToFile(FILE_REL_LEX_CSV, line)

def genRelTermTbl_sem(TermTbl):
    print "generate related-terms table"
    cdf_ttl2ttl = fif.load_json('pdb/pm_cdf_ttl2ttl.json')
    cdf_ttl2abs = fif.load_json('pdb/pm_cdf_ttl2abs.json')
    FILE_REL_CSV = 'pdb/pm_relatedterms_semantic.csv'
    fif.resetFile(FILE_REL_CSV)
    for ref_term, df in cdf_ttl2ttl.items():

        # related terms by CDF of TITLE
        relTtl = sorted(df.items(), key=lambda(k,v):v, reverse=True)[:8]
        relTtl = [t for (t, cnt) in relTtl]
        relTtl_str = '|'.join(['%s;%s'%(t,TermTbl.get(t,0)) for t in relTtl])

        # related terms by CDF of ABSTRACT
        dfa = cdf_ttl2abs.get(t,None)
        if not dfa: continue
        relAbs = sorted(dfa.items(), key=lambda(k,v):v, reverse=True)[:15]
        relAbs = [t for (t,cnt) in relAbs]
        relAbs_str = '|'.join(['%s;%s'%(t,TermTbl.get(t,0)) for t in relAbs])

        line = '%s,%d,%s,%s'%(ref_term, TermTbl.get(ref_term,0), relTtl_str, relAbs_str)
        fif.addLineToFile(FILE_REL_CSV, line)

def genTerm2Paper(termtbl):
    print "generate term2paper table"
    # load exiting term->paper_id
    t2p = fif.load_json('pdb/pm_idx_t2p_ttl.json')
    FILE_T2P_CSV = 'pdb/pm_index_t2p.csv'
    fif.resetFile(FILE_T2P_CSV)
    for t, plist in t2p.items():
        if not t: continue
        if not len(plist)>1: continue
        if len(plist)>2000: continue # TODO: think about this
        tid = termtbl[t]
        plist_str = ','.join(plist)
        line = '%s,%d,"%s"'%(t, tid, plist_str)
        fif.addLineToFile(FILE_T2P_CSV, line)

def generateTables():
    ttbl = fif.load_json('pdb/pm_term_tbl.json')
    genTblPaperTerm(ttbl)
    #genRelTermTbl_sem(ttbl)
    #genRelTermTbl_lex(ttbl)
    #genTerm2Paper(ttbl)

if __name__=='__main__':
    generateTables()
