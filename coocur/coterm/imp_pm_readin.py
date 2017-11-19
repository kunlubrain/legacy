import re
import imp_pm_psr as psr
import ctypes # for postive hash code
import fif

FilePaper = 'TblPaper.txt'
FileAuthor = 'TblAuthor.txt'
FileHash2Id = 'TblHash2Id.json'
FilePid2Term = 'TblPidTerms.txt'
FilePublisher = 'TblPublisher.txt'
FileOrg = 'TblOrg.txt'

def getmeta(line):
    return re.split(r'![A-Z]\$', line)

def papermeta():
    with open(FilePaper, 'r') as f:
        for line in f:
            yield getmeta(line)

def getPublisherId2Name():
    return getId2Name(FilePublisher)

def getAuthorId2Name():
    return getId2Name(FileAuthor)

def getId2Name(Filename):
    print "getId2Name: read-in", Filename
    id2name = {}
    with open(Filename, 'r') as f:
        for line in f:
            fields = re.split(r'![A-Z]\$', line)
            iid, nm = fields[1], fields[2].strip('\n')
            id2name[iid]=nm
    return id2name

def getAuthorId2X(fieldIndex):
    #
    # get a mapping: authorId --> [id of sth else]
    # $fieldIndex - where the target data cell is in the author file
    #
    id2x = {}
    with open(FileAuthor, 'r') as f:
        for line in f:
            fields = re.split(r'![A-Z]\$', line.strip('\n'))
            iid, x = fields[1], fields[fieldIndex].split(',')
            id2x[iid]=x
    return id2x

def getAuthorId2Org():
    print "getAuthorId2Org: read-in", FileAuthor
    return getAuthorId2X(-2)

def getAuthorId2Paper():
    print "getAuthorId2Paper: read-in", FileAuthor
    return getAuthorId2X(-1)

def __cityAndCountry(geoTex):
    fields = geoTex.split(',', 1)
    if not len(fields)>1:
        if re.search(r'\w+\s+\d+', geoTex): # CITY + POSTAL
            city = re.sub('\s+\d+','',geoTex) # remove the postal
            return city, None
        return None, geoTex
    city = fields[0]
    city = re.sub('\s+\d+','',city) # remove the postal
    if not re.search(r'^[A-Z][^A-Z]', city): city = None
    country = fields[1].split(',')[-1].split(';')[0]
    if re.search(r'\d+', country):
        country = None
    else:
        if not re.match(r'^[\w\.\d]+$', country): country = None
    return city, country

# RETURN: org_id --> [depart, orgnization, city, country, geotext]
def getOrgId2Data():
    with open(FileOrg, 'r') as f:
        for line in f:
            fields = line.split('#',3)
            iid = fields[0]
            depart = fields[1]
            org = fields[2]
            geo = fields[3].strip('\n').strip(';')
            city, country = __cityAndCountry(geo)
            yield (iid, depart, org, city, country, geo)

def getPaperIdYearPubTtl():

    PaperIdYearPub = {}
    with open(FilePaper, 'r') as f:
        for line in f:
            fields = re.split(r'![A-Z]\$', line)
            pid  = fields[1]
            year = fields[2]
            year = re.search(r'\d{4}', year).group(0)
            puid = fields[4]
            ttl  = fields[5]
            ttl = ttl.replace('\n', '')
            ttl = re.sub(r'[\s\t]+', ' ', ttl)
            ttl = ttl.lower()
            ttl = ttl.rstrip('.')
            PaperIdYearPub[pid] = [year, puid, ttl]

    return PaperIdYearPub

def makeHash(ttl, year):
    initiate = ''.join([w[0] for w in ttl.split() if re.match(r'\w', w[0])])
    code = initiate + year[-2:]
    return ctypes.c_size_t(hash(code)).value

def getPaperHashYearTTl():
    hash2yearttl={}
    for pmeta in psr.papermeta():
        h=pmeta[0]
        y=pmeta[1]
        t=pmeta[4]
        hash2yearttl[h]=[y,t]
    return hash2yearttl

def hashcode2PubmedId():

    print "make dict:  id --> year, pub, ttl"
    pidYearPubTtl = getPaperIdYearPubTtl()

    print "make dict:  hash --> year, ttl"
    phashYearTtl  = getPaperHashYearTTl() # old data with hash-id
    badRecords = []
    hash2Pid = {}

    for pid, fields in pidYearPubTtl.items():
        year, ttl = fields[0], fields[2]

        # compute the hash code and make mapping hashcode -> pid
        h = makeHash(ttl, year)

        # check that the hash-code hashed to the same paper
        if not h in phashYearTtl:
            badRecords.append('%s!%s!%s'%(pid,year,ttl))
        else:
            oldffields = phashYearTtl[h]
            oldyear = str(oldffields[0])
            oldttl = oldffields[1]
            test1 = oldyear == year
            test2 = oldttl[:5] == ttl[:5]
            if not test1:
                print "different year"
                print "old year:", oldyear, "type=",type(oldyear)
                print "year:", year, "type=",type(year)
                raw_input()
        hash2Pid[h] = pid

    # save them to a file
    fif.save_json(FileHash2Id, hash2Pid)
    fif.saveIterable('TblHash2IdBad.txt', badRecords)

def overwrite():
    hash2pid = readPaperHash2Id()
    badRecord = '!NO HASH IN HASH2PID!'
    fif.resetFile(FilePid2Term)
    for pt in psr.paperterms():
        hashid, termTtl, termAbs = pt[0], pt[1], pt[2]
        if hashid in hash2pid:
            pid = hash2pid[hashid]
            tterm = ';'.join(termTtl)
            aterm = ';'.join(termAbs)
            text = '%s!%s!%s'%(pid,tterm,aterm)
            fif.addToFile(FilePid2Term, text, isline=1)
        else:
            badRecord += "%s\n"%hashid
    with open('BadHash2Pid.txt', 'w') as f: f.write(badRecord)

def readPaperHash2Id():
    return fif.load_json(FileHash2Id)

def paperterms():
    def parseline(line):
        fields = line.split('!')
        assert len(fields)==3
        pid = fields[0]
        termttl = fields[1]
        termabs = fields[2]
        return (pid, termttl.split(';'), termabs.split(';'))

    with open(FilePid2Term, 'r') as f:
        for line in f:
            yield parseline(line)

if __name__=='__main__':
    #hashcode2PubmedId()
    overwrite()
