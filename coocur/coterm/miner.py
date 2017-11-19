import compiler
import inferencer as inf
from optparse import OptionParser

DEBUG_INFERENCE=1

def mine(resetpdb, importpdb, paperfile):

    # === IMPORT ===
    if resetpdb:
        import importer_pubmed as pm
        pm.resetPDB()
        return
    if importpdb:
        import importer_pubmed as pm
        pm.importing(pubmed_papers=paperfile)

    # === COMPILE ===
    compiler.main()


    # === INFER ===
    inf.main()

if __name__=='__main__':
    optparser = OptionParser()
    optparser.add_option('-r', '--resetpdb', dest='reset', action='store_true', default=False)
    optparser.add_option('-i', '--importpdb', dest='imprt', action='store_true', default=False)
    optparser.add_option('-p', '--paperfile', dest='pfile', default='pubmed_result.txt')

    (opt, args)=optparser.parse_args()

    mine(opt.reset, opt.imprt, opt.pfile)

# TODO
# - use Logger for debugging
# - handling captalization, plural, verb singlar form
# -
# IDEA:
# if the DF of a term in abstract is larger than that in title,
# ==> implies this term is not specific enough for the topic in title
#
# - remove the empty term ''
#
# - consider N-Gram when doing df
