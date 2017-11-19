import fif as fif


FILE_TERM_DFT = "pdb/pm_df_t_ttl_2.json"
FILE_TERM_DFA = "pdb/pm_df_t_abs_2.json"
FILE_TERM_TBL_CSV = "pdb/pm_term_tbl.csv"
FILE_TERM_TBL_JSON= "pdb/pm_term_tbl.json"


# generate a term table: termid, termname
# because now we only consider terms with more than 2 occurance,
# thus putting this function in compiler after df
def makeTable():

    dftt=fif.load_json(FILE_TERM_DFT)
    dfta=fif.load_json(FILE_TERM_DFA)
    terms=dftt.keys()+dfta.keys()

    tid, this_id = {}, 1
    for t in terms:
        if not t in tid:
            tid[t]=this_id
            this_id+=1
    print "termtbl size",len(tid)

    fif.resetFile(FILE_TERM_TBL_CSV)
    fif.addLineToFile(FILE_TERM_TBL_CSV, "termid, term")
    for t, _id in tid.items():
        fif.addLineToFile(FILE_TERM_TBL_CSV, '%d,"%s"'%(_id, t))
    fif.save_json(FILE_TERM_TBL_JSON, tid)

if __name__=='__main__':
    makeTable()
