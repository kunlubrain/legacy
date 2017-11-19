import fif
import re

termfile = 'tmp_ieee_coocur_abstractwide_gramstest.txt'
termfile = 'tmp_ieee_coocur_abstractwide_grams.txt'
termfile = 'tmp_ieee_coocur_selected.txt'

TwoGramFileDot = "TwoGram2Term_ieee.dot"

cobook = fif.readCoocurWithFilterFunc(termfile, None, filtervalue=2)

KeyTerms = {}

def writefile(fname, line):
    with open(fname, 'a') as fh:
        fh.write(line+'\n')

print "here we go ..."

for term, hist in cobook.items():
    related = hist.keys()

    if len(term)<2: continue

    def __good(rel, term):
        if len(rel.split())>5: return 0
        if rel in term: return 0
        if rel.strip('s') in term: return 0
        containedIn = 1
        for w in rel.split():
            if not w in term:
                containedIn = 0
        if containedIn: return 0
        if "important" in rel: return 0
        if "difficulty" in rel: return 0
        if "good" in rel: return 0
        if "role" in rel: return 0
        if "let" in rel: return 0
        if "idea" in rel: return 0
        if len(rel)<2: return 0
        #if not re.match('^[\w-]$', rel): return 0
        return 1

    # select good related terms
    rel = set([t for t in related if __good(t, term)])
    rel_taken = set([])
    for rr in rel:
        alreadyIn = False
        toremove = []
        for rrr in rel_taken:
            if rr in rrr: alreadyIn=True
            if rrr in rr: toremove.append(rrr)
        if not alreadyIn: rel_taken.add(rr)
        for rrr in toremove: rel_taken.remove(rrr)

    rel = rel_taken

    if not len(rel)>1: continue

    KeyTerms[term] = rel

print "KeyTerm size", len(KeyTerms)

raw_input('...')

# build some 2-grams
TwoGram2Term = {}
for t in KeyTerms:
    words = t.split()
    if len(words)<3: continue
    for i, w in enumerate(words[:-1]):
        twogram = words[i] + " " + words[i+1]
        if not twogram in TwoGram2Term:
            TwoGram2Term[twogram] = []
        TwoGram2Term[twogram].append(t)

print "Twogram size", len(TwoGram2Term)

with open(TwoGramFileDot, 'w') as f:
    f.write("digraph semnet {\n")

writefile(TwoGramFileDot, "rankdir = LR;")

i = 0
for tg, terms in TwoGram2Term.items()[:500]:

    if not 'differential equations' in tg: continue

    if len(terms)>3:
        termquoted = set(['"%s"'%t for t in terms])

        hist, nRel ={}, 0
        for t in terms:
            for rr in KeyTerms[t]:
                hist[rr] = hist.get(rr, 0) + 1
                nRel += 1
        print "num. related terms:", nRel, "num. uniq terms:", len(hist)
        if not nRel > len(hist)+3:
            continue

        i+=1

        line = '"%s" -> {%s}'%(tg,'; '.join(termquoted))
        print "###",line
        writefile(TwoGramFileDot, line)
        for t in terms:
            rel = KeyTerms[t]
            relquoted = ['"%s"'%r for r in rel]
            line = '"%s" -> {%s}'%(t,"; ".join(relquoted))
            writefile(TwoGramFileDot, line)
            print "term:", t
            print "line:", line
            #raw_input("...")
print "total", i, "terms"

writefile(TwoGramFileDot, "}")
