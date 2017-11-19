#
# This file contains glue code to parse the stored paper info for the compiler
#
import fif as fif

PM_TERM_FILE = 'deprecated/pdb_pubmed_kw.py'
PM_META_FILE = 'deprecated/pdb_pubmed_meta.py'

#  DEPRECATED !!!
def parseTermLine(_line):
    # A line has such structure:
    # (paper id, {term:count}, {term:count},    {word:count}, {word:count})
    #             ^-- in title  ^-- in abstract ^-- in title  ^-- in abstract
    line = _line.replace('{}',"{'_':1}") # some title has no terms: {}
    line = line.replace('"',"'").replace("{'",'##').replace("},", "")
    line = line.replace('}),\n','').replace("'","").replace('(','').split("##")

    try:
        pid = line[0].replace('L,','').strip()
        termTtl = [r.split(':')[0].strip() for r in line[1].split(',')]
        termAbs = [r.split(':')[0].strip() for r in line[2].split(',')]
        wordTtl = [r.split(':')[0].strip() for r in line[3].split(',')]
        wordAbs = [r.split(':')[0].strip() for r in line[4].split(',')]
    except:
        print "BAD TERM LINE", _line
        return (None, [], [], [], [])
    return (pid, termTtl, termAbs, wordTtl, wordAbs)

#  DEPRECATED !!!
def parseMetaFrom(line):
    _line = line.replace('[],',"[']").replace('"]',"']") # some has no author []
    meta_title_abs = _line.split("']")
    if not len(meta_title_abs)>1: return None,None,None,None,None,None

    meta = meta_title_abs[0].split('[')
    ttl_abs = meta_title_abs[1].split(", [")
    ttl = ttl_abs[0].strip("',) ").replace('"',"'")
    abstract = ttl_abs[1].strip("'],)")

    id_year_jnl = meta[0].split(',')
    _id         = id_year_jnl[0].replace('(','').replace('L','')
    _id         = int(_id)
    _year       = int(id_year_jnl[1].replace("'",'').strip())
    _jnl        = id_year_jnl[2].replace("'",'').strip()
    authors     = meta[1].replace('"',"'").split("', ")
    authors     = [a.strip("'") for a in authors if len(a)>1]

    return (_id, _year, _jnl, authors, ttl, abstract)

# Some papers have the same Initiative and Year !!!
def removeDuplicatedRecord():
    existingHash = {}
    newfile = 'deprecated/pdb_pubmed_term_uniqhash.py'
    newfile_bad = 'deprecated/pdb_pubmed_term_duplicatedhash.py'
    print "uniqification of", newfile
    with open(PM_TERM_FILE, 'r') as f:
        for line in f:
            break
            pt = parseTermLine(line)
            hashid = pt[0]
            if not hashid: continue
            if not hashid in existingHash:
                existingHash[hashid]=1
                with open(newfile, 'a') as f:
                    f.write(line)
            else:
                print "duplicated hashid", hashid
                with open(newfile_bad, 'a') as f:
                    f.write(line)

    existingHash = {}
    newfile = 'deprecated/pdb_pubmed_meta_uniqhash.py'
    newfile_bad = 'deprecated/pdb_pubmed_meta_duplicatedhash.py'
    print "uniqification of", newfile
    with open(PM_META_FILE, 'r') as f:
        for line in f:
            fields = line.split(',')
            if not len(fields) > 1: continue
            hashid = fields[0].strip('(').strip('L')
            if not hashid: continue
            if not hashid in existingHash:
                existingHash[hashid]=1
                with open(newfile, 'a') as f:
                    f.write(line)
            else:
                print "duplicated hashid", hashid
                with open(newfile_bad, 'a') as f:
                    f.write(line)


#TODO - simplify or merge this function with the indexing in cmpl_index,parseTermLinein impt_parse, etc
def loadP2T(what):
    print "load paper2term from", PM_TERM_FILE, "using", what
    __rP2TTtl = {}
    with open (PM_TERM_FILE, 'r') as f:
        for line in f:
          pid, termTtl, termAbs, wordTtl, wordAbs = parseTermLine(line)
          if not pid: continue
          if what=='ttl':   __rP2TTtl[pid]=termTtl
          elif what=='abs': __rP2TTtl[pid]=termAbs
    return __rP2TTtl

def getPprId(resultsFrom_parseTermLine): return resultsFrom_parseTermLine[0]
def getTermListTtl(resultsFrom_parseTermLine): return resultsFrom_parseTermLine[1]
def getTermListAbs(resultsFrom_parseTermLine): return resultsFrom_parseTermLine[2]

def paperterms():
    with open(PM_TERM_FILE, 'r') as f:
        for line in f:
            yield parseTermLine(line)

def postprocess():

    print "make paper table: paperid, year, journal, title, authors, authorids"

    # load existing author table
    AuthTblFile       ='pdb/pm_author_count.csv'
    atbl = fif.loadCSV(AuthTblFile)

    FILE_PPRMETA_CSV = "pdb/pm_paper_meta.csv"
    fif.resetFile(FILE_PPRMETA_CSV)
    fif.addLineToFile(FILE_PPRMETA_CSV, "paperid,year,journal,title,authors")

    #TODO-put journal table generation from compiler to importer
    jnl_name2id = fif.loadCSV('pdb/pm_jnl.csv')

    # load and process each paper
    for pt in papermeta():
        _id, _year, _jnl, authors, ttl, abstract = pt
        if not _id: continue
        if not ttl: ttl='-'

        _idstr=str(_id).strip('L')
        jnlid=jnl_name2id.get(_jnl,0)
        _linemeta = '%s,%s,%s,"%s",'%(_idstr, _year, jnlid, ttl)


        if not authors:
            authortext='"-;0"'
        else:
            authortext='"%s"'%'|'.join(['%s;%s'%(a, atbl.get(a,0)) for a in authors])

        _linemeta += authortext
        fif.addLineToFile(FILE_PPRMETA_CSV, _linemeta)

if __name__=='__main__':
    postprocess()
