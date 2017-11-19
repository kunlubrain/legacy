import cmpl_df as dfreq
import cmpl_index as idx
import cmpl_auth_tbl as auth_tbl
import cmpl_term_tbl as term_tbl

def main():

    # Indexing
    idx.indexing()

    # Document frequency
    dfreq.df()

    # Tables for one authors
    auth_tbl.makeTable()

    # TODO - find "noisy" terms whose df is above above x after calling df

    # Tables for each term
    term_tbl.makeTable()

if __name__=='__main__':
    main()


# assemble: gather together at one place
# compile:  assemble, collect, summerize and report, eg. make a list of info
