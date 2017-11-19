import re
import fif
import imp_pm_datamodel as dm

import pickle

# FILEs to write to
#

FileTblPaper  = 'TblPaper.txt'   # <tbl1> ID, TTL, ABS, YEAR, PUBID, [AUID]
FilePaperPkl  = 'TblPaper.pkl'   # <tbl1> ID, TTL, ABS, YEAR, PUBID, [AUID]

FileTblAuthor = 'TblAuthor.txt'  # <tbl2> AUID - NAME, [INSTID]
FileAuthorPkl = 'TblAuthor.pkl'  # <tbl2> AUID - NAME, [INSTID]

FileTblDepart = 'TblOrg.txt'     # <tbl3> INSTID - text, geo
FileDepartPkl = 'TblOrg.pkl'     # <tbl3> INSTID - text, geo

FileTblPub    = 'TblPublisher.txt'     # <tbl4> PUBID - NAME
FilePubPkl    = 'TblPublisher.pkl'     # <tbl4> PUBID - NAME


AuthorName2Id = dm.AuthorRec()
Publisher_Name2Id = dm.PublisherRec()
Depart_Name2Id = dm.DepartRec()


def parse(paperRecord):
    paperText = paperRecord.replace('\n     ','')
    paperText = re.sub('\s\s+',' ',paperText)
    #print paperText

    pmid,ttl,bttl,abst,date,jnl,ptyp = 0,0,0,0,0,0,0

    for line in paperText.split('\n'):
        tag = line[:5]
        if   tag == 'PMID-': pmid = line[5:].strip()
        elif tag == 'TI - ': ttl  = line[5:]
        elif tag == 'BTI -': bttl = line[5:]
        elif tag == 'AB - ': abst = line[5:]
        elif tag == 'DP - ': date = line[5:]
        elif tag == 'JT - ': jnl  = line[5:] # book has no jt
        elif tag == 'PT - ': ptyp = line[5:]

    if not date or not ttl or not abst: return -1
    year = re.search(r'\d\d\d\d', date).group(0)

    # make id for publisher

    pubid = Publisher_Name2Id.add(jnl)

    # make id for authors
    # make id for authors' organization (an author may have null organization)

    authorData = {} # author -> [author department]
    AuthorRegex = '((FAU -.*\n)(AU.*\n)?(AD -.*\n)?)'
    authorText = re.findall(AuthorRegex, paperText)

    #print "authortext", authorText

    if not authorText: return -1

    for a in authorText:
        textMatched = a[0]
        name = re.search('FAU - (.*?)\n', textMatched).group(1)
        matchDept = re.search('AD - (.*?)\n', textMatched)
        if matchDept:
            dept = matchDept.group(1)
            dept = [d.strip(' .') for d in re.split('\[?\d\]', dept) if d]
            authorData[name] = dept
        else:
            authorData[name] = []

    #TODO - multiple departments in form of multiple AD instead of [1],[2],etc
    #print "authordata", authorData

    # make id for publisher, authors
    id_auths = [ '%s:%s'%(nm,AuthorName2Id.add(nm)) for nm in authorData]

    # make id for author department
    # loop: author_name -> [departments]
    for nm, depts in authorData.items():

      joinedDepartIds = ','.join(['%s'%Depart_Name2Id.add(d) for d in depts])

      AuthorName2Id.addDepart(nm, joinedDepartIds)
      AuthorName2Id.addPaper(nm, pmid)

      authorText = ';'.join(['%s'%i for i in id_auths])

    #paperRec = "!I$%s!Y$%s!P$%s!B$%s!T$%s!A$%s!U$%s!D$=%s"%(pmid, year, jnl, pubid, ttl, abst,
    #                                                   authorText, date)

    #fif.addToFile(FileTblPaper, paperRec, isline=1)

    return {'id':pmid, 'year':year, 'pub':jnl, 'pub_id':pubid, 'title':ttl, 'abstract':abst}

def dump2file():

    print "dump file", FileTblAuthor
    for rec in AuthorName2Id.nextRecText():
        fif.addToFile(FileTblAuthor, rec, isline=1)

    print "dump file", FileTblDepart
    for rec in Depart_Name2Id.nextRecText():
        fif.addToFile(FileTblDepart, rec, isline=1)

    print "dump file", FileTblPub
    for rec in Publisher_Name2Id.nextRecText():
        fif.addToFile(FileTblPub, rec, isline=1)

def dump2pickle():

    with open(FileAuthorPkl, 'w') as fh:
        pickle.dump(AuthorName2Id.get(), fh)
    print "saved to", FileAuthorPkl

    with open(FilePubPkl, 'w') as fh:
        pickle.dump(Publisher_Name2Id.get(), fh)
    print "saved to", FilePubPkl

    with open(FileDepartPkl, 'w') as fh:
        pickle.dump(Depart_Name2Id.get(), fh)
    print "saved to", FileDepartPkl

def extractPapers(pubmedFile='pmed/pubmed_1996.txt'):
    pubmedFile='pubmed_result.txt'
    pubmedFile='pmed/pubmed_neurosci.txt'
    print "extract papers from", pubmedFile

    fif.resetFile(FileTblPaper)
    fif.resetFile(FileTblAuthor)
    fif.resetFile(FileTblDepart)
    fif.resetFile(FileTblPub)

    papertext=''
    print "crunching", pubmedFile
    papers = []
    with open(pubmedFile, 'r') as fh:
      for i, line in enumerate(fh):
          if line[0:5] == 'PMID-':
            p = parse(papertext)
            papers.append(p)
            papertext=''
          papertext += line

          if Publisher_Name2Id.len()>5e10:
              break
    print "crunching done"

    with open(FilePaperPkl, 'w') as fh:
        pickle.dump(papers[1:], fh)
    print "saved to", FilePaperPkl

    #dump2file()
    dump2pickle()
    print "extract papers - ALL DONE\n"

if __name__=='__main__':
    extractPapers()

# when joining the lines: crazy random output when doing
# papertext += line.strip('\n')+'\n'
