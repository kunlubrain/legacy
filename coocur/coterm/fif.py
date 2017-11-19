import json
import codecs

# Items of these files should be created and deleted together (for each paper)
PAPER_KW_FILE   = 'pdb_pubmed_kw.py'
PAPER_META_FILE = 'pdb_pubmed_meta.py'
PAPER_ID_FILE   = 'pdb_pubmed_id.py'  # id of processed papers

def resetPDB(item='PAPERS'):
    print "reset pdb ..."
    def __reset(filename):
        with open(filename, 'w') as fh:
            fh.write('%s=[\n]\n'%item)
    __reset(PAPER_ID_FILE)
    __reset(PAPER_META_FILE)
    __reset(PAPER_KW_FILE)

def reset(filename, item):
    print "reset file for %s ..."%filename
    with open(filename, 'w') as fh:
        fh.write('%s=[\n]\n'%item)

def insertLine2PdbFile(filename, line):
    with open(filename, 'r+b') as fh:
        fh.seek(-2,2) # '2' seek backward
        assert fh.read(1)==']', 'BAD FORMAT! Last character must be ].'
        fh.seek(-2,2) # '2' seek backward
        line += '\n]\n'
        fh.write(line)

def save_json(filename, data):
    print "save %s, DataType %s"%(filename, type(data))
    with open(filename, 'w') as fh:
        json.dump(data, fh)

def load_json(filename):
    print "load %s"%filename
    with open(filename, 'r') as fh:
        return json.load(fh)

def resetFile(filename):
    print "reset %s"%filename
    with codecs.open(filename, 'w', 'utf-8') as fh: fh.write('')

def addLineToFile(filename, line):
    with codecs.open(filename, 'a', 'utf-8') as fh: fh.write(line+'\n')

def addToFile(filename, line, isline=0):
    if isline:
        with codecs.open(filename, 'a', 'utf-8') as fh: fh.write(line+'\n')
    else:
        with codecs.open(filename, 'a', 'utf-8') as fh: fh.write(line)

def loadCSV(filename):
    print "load file ", filename
    _d = {}
    with open(filename, 'r') as fh:
        for line in fh:
            fields = line.split(',', 1)
            try:
                _d[fields[1].split('"')[1]]=fields[0]
            except: continue
    return _d

def saveIterable(fname, iterable):
    with open(fname, 'w') as fh:
        for r in iterable:
            fh.write(r+'\n')
