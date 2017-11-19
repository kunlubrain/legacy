import imp_pm_readin as readin
import fif

FileSqlPaper       = 'pdb/SqlPaper.csv'
FileSqlAuthor      = 'pdb/SqlAuthor.csv'
FileSqlAuthorOrg   = 'pdb/SqlAuthorOrg.csv'
FileSqlAuthorPaper = 'pdb/SqlAuthorPaper.csv'
FileSqlPub         = 'pdb/SqlPublisher.csv'
FileSqlOrg         = 'pdb/SqlOrg.csv'

def sqlization(x): return '"%s"'%x.replace('"', '\"')

def makeSqlTblPaper():

    print "\nmake === PAPER TABLE ==="

    # paperid, year, publisher, title, abstract, authors
    fif.resetFile(FileSqlPaper)
    print "dump each record line ..."
    for meta in readin.papermeta():
        iid     = meta[1]
        year    = meta[2]
        pub     = sqlization(meta[3])
        pubid   = sqlization(meta[4])
        ttl     = sqlization(meta[5])
        abstr   = sqlization(meta[6])
        authors = sqlization(meta[7])
        # save them to the csv
        line = ','.join([iid,year,pub,pubid,ttl,abstr,authors])
        fif.addToFile(FileSqlPaper, line, isline=1)

def _dumpId2Name(id2name, filename):
    fif.resetFile(filename)
    print "dump each record line ..."
    for iid, name in id2name.items():
        line = '%s,%s'%(iid, sqlization(name))
        fif.addToFile(filename, line, isline=1)

def makeSqlTblPublisher():

    print "\nmake === PUBLISHER TABLE ==="

    # publisherid, publihsername
    id2Name = readin.getPublisherId2Name()
    _dumpId2Name(id2Name, FileSqlPub)

def makeSqlTblAuthor():

    print "\nmake === AUTHOR TABLE ==="

    # authorid, authorname
    id2Name = readin.getAuthorId2Name()
    _dumpId2Name(id2Name, FileSqlAuthor)

def __dumpId2IdList(filename, id2IdList):
    fif.resetFile(filename)
    print "dump each record line ..."
    for iid, idlist in id2IdList.items():
        if not idlist: continue  # could be empty for author->org
        for iiid in idlist:
            line = '%s,%s'%(iid, iiid)
            fif.addToFile(filename, line, isline=1)

def makeSqlTblAuthorOrg():

    print "\nmake === AUTHOR-2-ORGANIZATION TABLE ==="

    authorId2OrgIds = readin.getAuthorId2Org()
    __dumpId2IdList(FileSqlAuthorOrg, authorId2OrgIds)

def makeSqlTblAuthorPaper():

    print "\nmake === AUTHOR-PAPER TABLE ==="

    authorId2PaperIds = readin.getAuthorId2Paper()
    __dumpId2IdList(FileSqlAuthorPaper, authorId2PaperIds)

def makeSqlTblOrg():
    fif.resetFile(FileSqlOrg)
    # id, org-department, orgnization, city, country, georawtext
    for data in readin.getOrgId2Data():
      try:
        iid, depart, org, city, country, geo = data
        #print "orgline", iid, depart
        #print "       > org= ", org
        #print "       > city=", city
        #print "       > co=  ", country
        #print "       > geo= ", geo
        line = '%s,%s,%s,%s,%s,%s'%(iid, sqlization(depart), sqlization(org), city, country, sqlization(geo))
        line = '%s,%s,%s,%s,%s'%(iid, sqlization(depart), sqlization(org), city, country)
        fif.addToFile(FileSqlOrg, line, isline=1)
      except:
        print("BADLINE when making sql for organization", line)
    print "- DONE"

def makeSqlTable():

    #makeSqlTblPaper()
    #makeSqlTblAuthor()
    #makeSqlTblAuthorPaper()
    #makeSqlTblPublisher()
    #makeSqlTblAuthorOrg()
    makeSqlTblOrg()

if __name__=='__main__':
    makeSqlTable()

#
# make tables
# - paper table
#   paperid, year, publisher, title, abstract, authors-text
#   24124,   2010, nature,    xxx,   abc     , (nm:id;)*

# - paper term table
#   paperid, terms-ttl, terms-abs
#   23424,   (nm:id;)*  (nm:id;)*
# NOTE:
# put it in an extra table because i need to select only the significant terms
# of a paper, thus can only be done by the inferencer
#
# - author-paper
#   authorid  paperid  year  publisher
#   1212      2342     2011  nature
#
# - author-table
#   authorid  authorname
#   342342    xxx
#
# - author-depart
#   authorid  departid
#   38383     798787
#
#
# - depart-table
#   departid   text    city country
#   889283     xxx     ulm  uk

