# Module Funtionality:
#  - conditional document frquency
#  - make networks and graphs
#  - relatedness

import inf_rel as rel
import inf_cdf as cdfreq
import inf_tbl as tbl

def main():
    rel.relatedTermByLexicon(TermJson='pdb/pm_df_t_ttl.json',
                             Word2TermJson='pdb/pm_idx_w2t_ttl.json',
                             Save2Json='pdb/pm_rel_t_ttl.json')
    rel.relatedTermBySyntax()
    rel.headwording(TermJson='pdb/pm_df_t_ttl.json',
                    Save2Json='pdb/pm_rel_head_ttl.json')

    cdfreq.cdf_ttl2ttl()
    cdfreq.cdf_ttl2abs()

    tbl.generateTables()

if __name__=='__main__':
    main()
