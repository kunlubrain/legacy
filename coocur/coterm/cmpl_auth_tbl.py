#
# Generate the AUTHOR TABLEs
#

import stat_counter as counter
import util as util
import fif as fif
import imp_pm_psr as psr

FILE_ATBL_CNT_JSON = "pdb/pm_author_count.json"
FILE_ATBL_YR_JSON  = "pdb/pm_author_year_count.json"
FILE_ATBL_JNL_JSON = "pdb/pm_author_jnl_count.json"

def makeId(name, name2id):
    if name in name2id: return
    name2id[name] = len(name2id)+1 # generate the new id

# author table
# journal table
# author-count table
# author-journal-count table
# author-year-count table
# author-year-journal-count table
def makeTable(SaveJson=False):
    def _append2d(d, k1, k2, v):
        if not k1 in d: d[k1]={}
        if not k2 in d[k1]: d[k1][k2]=[]
        d[k1][k2].append(v)

    # 2-D paper profile of authors: author->yearr->jnl->[pid]
    def _author2DProfile(profile, auth, yr, jnl, pid):
        if not auth in profile:             profile[auth]={}
        if not yr   in profile[auth]:       profile[auth][yr]={}
        if not jnl  in profile[auth][yr]:   profile[auth][yr][jnl]=[]
        profile[auth][yr][jnl].append(pid)

    authorCnt          = {} # author_name -> count
    authorYearCount    = {} # author_name -> year -> [paper id]
    authorJounralCount = {} # author_name -> journal -> [paper id]
    authorYrJnlCnt     = {} # author_name -> year -> jnl -> [paper id]
    author_id          = {} # stores author_name -> id
    journal_id         = {} # stores journal_name -> id

    print "author table generation using data from",psr.PM_META_FILE
    for pmeta in psr.papermeta():
        pid, _year, _jnl, authors, ttl, abstr = pmeta
        if not pid: continue

        makeId(_jnl, journal_id)
        for a in authors:
            makeId(a, author_id)
            counter.inc(authorCnt, a)
            _append2d(authorYearCount, a, _year, pid)
            _append2d(authorJounralCount, a, _jnl, pid)
            _author2DProfile(authorYrJnlCnt, a, _year, _jnl, pid)
        #if(len(authorCnt)>500): break
    print "Size of authortable", len(authorCnt)

    # save csv
    # AUTHOR TABLE:                     id name institution_id papercount
    # AUTHOR PAPER PER YEAR TABLE:      id name year count [paper_id]
    # AUTHOR PAPER PER JOURNAL TABLE:   id name journal_id count [paper_id]
    JournalFile    ='pdb/pm_jnl.csv'
    AuthFile       ='pdb/pm_author.csv'
    AuthCntFile    ='pdb/pm_author_count.csv'
    AuthJnlFile    ='pdb/pm_author_jnl_count.csv'
    AuthYearFile   ='pdb/pm_author_year_count.csv'
    AuthYearJnlFile='pdb/pm_author_year_jnl_count.csv'

    def __saveIdCsv(filename, idtbl):
        fif.resetFile(filename)
        fif.addLineToFile(filename, "id, name")
        for name, id_ in idtbl.items():
            line='%s,"%s"'%(id_, name)
            fif.addLineToFile(filename, line)
    #TODO - de-couple the generation of authorid with other author tables
    #TODO - use authorid->(name,papercount) as the authortable, ie. merge them
    #__saveIdCsv(AuthFile, author_id)
    #__saveIdCsv(JournalFile, journal_id)

    fif.resetFile(AuthCntFile)
    fif.resetFile(AuthJnlFile)
    fif.resetFile(AuthYearFile)
    fif.resetFile(AuthYearJnlFile)
    fif.addLineToFile(AuthCntFile, "authorid, name, papercount")
    fif.addLineToFile(AuthJnlFile, "authorid, journalid, papercount, paperlist")
    fif.addLineToFile(AuthYearFile,"authorid, year, papercount, paperlist")
    fif.addLineToFile(AuthYearJnlFile,"authorid, year, journal, papercount, paperlist")
    def __str(plist): return ','.join([str(p).strip('L') for p in plist])
    for name, count in authorCnt.items():
        authorid=author_id[name]
        fif.addLineToFile(AuthCntFile, '%d,"%s",%d'%(authorid, name, count))

        if count>10: # authors with more than 10 papers

            line=''
            for jnl, plist in authorJounralCount[name].items():
                line+='%d,%d,%d,"%s"\n'%(authorid,journal_id[jnl], len(plist), __str(plist))
            fif.addToFile(AuthJnlFile, line)

            line=''
            for year, plist in authorYearCount[name].items():
                line+='%d,%d,%d,"%s"\n'%(authorid, year, len(plist), __str(plist))
            fif.addToFile(AuthYearFile, line)

            line=''
            for yr, p in authorYrJnlCnt[name].items():
                for j, plist in p.items():
                  line+='%d,%d,%d,%d,"%s"\n'%(authorid,yr,journal_id[j],len(plist),__str(plist))
            fif.addToFile(AuthYearJnlFile, line)

    if SaveJson:
        fif.save_json(FILE_ATBL_CNT_JSON, authorCnt)
        fif.save_json(FILE_ATBL_YR_JSON,  authorYearCount)
        fif.save_json(FILE_ATBL_JNL_JSON, authorJounralCount)

if __name__=='__main__':
    makeTable(SaveJson=False)
