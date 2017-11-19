import re

# word matrix
wm = {}
pl = [] # tmporary store of the profile

def relation(sentences, word):

    whatfor = {}
    forclause = {}

    pttn = '(\w+\s+%s\s+\w+\s*\w*)'%word
    pttn_forx = '([fF]or\s+.*[,\.])'

    for s in sentences:
        #print s
        mo = re.findall(pttn, s)
        if mo:
            reason = mo[0].split(word)[0]
            print mo[0]
            if not reason in whatfor:
                whatfor[reason] = 0
            whatfor[reason] += 1
        #else: print s

        continue
        mo = re.search(pttn_forx, s)
        if mo:
            clause = mo.group(0)[:50]
            if not clause in forclause:
                forclause[clause]=0
            forclause[clause]+=1

    pl.append(whatfor)

    print "*********%s profile**********"%word
    for i in whatfor.items():
        if i[1]>1:
            print i
    for i in forclause.items():
        print i

def relation_for(sentences):
    relation(sentences, 'for')

def relation_in(sentences):
    relation(sentences, 'in')

def relation_by(sentences):
    relation(sentences, 'by')

def relation_with(sentences):
    relation(sentences, 'with')

papers=['corpus.txt', 'test_paper1.txt', 'test_paper2.txt', 'test_paper3.txt',
        'test_paper4.txt', 'test_paper5.txt', 'test_paper6.txt','test_paper7.txt',
        'test_paper8.txt', 'test_paper9.txt']
for p in papers:
    with open(p, 'r') as fh: corpus = fh.read()
    sentences = corpus.split('.')
    #relation_for(sentences)
    #relation_in(sentences)
    #relation_by(sentences)
    #relation_with(sentences)
    #relation(sentences, 'than')
    #relation(sentences, 'into')
    #relation(sentences, 'between')
    #relation(sentences, 'among')
    #relation(sentences, 'within')
    #relation(sentences, 'without')
    #relation(sentences, 'before')
    #relation(sentences, 'after')
    #relation(sentences, 'and')
    #relation(sentences, 'therefore')
    #relation(sentences, 'thus')
    #relation(sentences, 'hence')
    #relation(sentences, 'although')
    #relation(sentences, 'though')
    #relation(sentences, 'onto')
    #relation(sentences, 'over')
    #relation(sentences, 'under')
    #relation(sentences, 'following')
    #relation(sentences, 'followed')
    #relation(sentences, 'during')
    #relation(sentences, 'beyond')
    #relation(sentences, 'through')
    #relation(sentences, 'at')
    #relation(sentences, 'from')
    #relation(sentences, 'except')
    #relation(sentences, 'outside')

    #relation(sentences, 'or')

    #relation(sentences, 'if')

    #relation(sentences, 'must')

    #relation(sentences, 'not')

    #relation(sentences, 'lead to')

    #relation(sentences, 'suggesting')

    #relation(sentences, 'To address this')

    #relation(sentences, 'Specifically')
    #relation(sentences, 'far more')
    #relation(sentences, 'only')
    #relation(sentences, 'better')

    #relation(sentences, 'based on')

    #relation(sentences, 'contrast')
    #relation(sentences, 'while')
    #relation(sentences, 'whereas')
    #relation(sentences, 'always')

    #relation(sentences, 'here')
    #relation(sentences, 'but')
    #relation(sentences, 'may')
    #
    #relation(sentences, 'using')
    #relation(sentences, 'because')
    relation(sentences, 'each')

    relation(sentences, 'demonstrate')
    relation(sentences, 'extreamly')
    relation(sentences, 'significant')

allwords = []
for p in pl: allwords += p.keys()
assert len(pl)==len(papers)
for w in allwords: wm[w]=[0]*len(pl)
for i, p in enumerate(pl):
    for w in allwords:
        if w in p:
            wm[w][i]=p[w]
        else:
            wm[w][i]=0

for i in wm.items():
    print i[0].ljust(30), ' '.join(['%s'%x for x in i[1]]).replace('0','_')
