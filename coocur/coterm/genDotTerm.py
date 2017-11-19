import fif
import re

termfile = 'pdb/pm_relatedterms_lexical.csv'
termfile = 'pdb/pm_relatedterms_semantic.csv'

File2GramDot = 'lex2gram_sem.dot2'

KeyTerms = {}

#TermCount = fif.load_json('pdb/pm_df_t_abs_3.json')

TmplTerm = '''
  "%s": {
    "weight": "%s",
    "type": "%s",
    "markup": "reserved",
    "relatedTerms": [%s
    ]
  },
'''

PaperText="Structural variants are genomic rearrangements larger than 50 bp accounting for around 1% of the variation among human genomes. They impact on phenotypic diversity and play a role in various diseases including neurological/neurocognitive disorders and cancer development and progression. Dissecting structural variants from next-generation sequencing data presents several challenges and a number of approaches have been proposed in the literature. In this mini review, we describe and summarize the latest tools - and their underlying algorithms - designed for the analysis of whole-genome sequencing, whole-exome sequencing, custom captures, and amplicon sequencing data, pointing out the major advantages/drawbacks. We also report a summary of the most recent applications of third-generation sequencing platforms. This assessment provides a guided indication - with particular emphasis on human genetics and copy number variants - for researchers involved in the investigation of these genomic events.".lower()

TmplRelTerm = '''
      {
        "name": "%s",
        "weightOfRelatedness": "%s",
        "docFreq": "%s",
      },'''

def writefile(filename, line):
    with open(filename,'a') as f:
        f.write(line+'\n')

with open(termfile, 'r') as f:

    jsonText = "{"

    numterms = 0
    for line in f:
        numterms+=1

        #if numterms>30: break

        tex = re.sub(r'([,;])\d+.?',';',line.strip('\n'))
        fields = tex.split(';',1)

        term = fields[0]

        #if not term in PaperText: continue
        #print "found term:   ", term
        #continue

        related = fields[1].strip(';').split(';')

        if len(term.split())<2: continue

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
            if "good" in rel: return 0
            if "role" in rel: return 0
            return 1

        # select good related terms
        rel = set([t for t in related if __good(t, term)])
        rel_taken = set([])
        for rr in rel:
            alreadyIn = False
            toremove = []
            for rrr in rel_taken:
                if rr in rrr:
                    alreadyIn=True
                if rrr in rr:
                    toremove.append(rrr)
            if not alreadyIn:
                rel_taken.add(rr)

            for rrr in toremove:
                rel_taken.remove(rrr)

        rel = rel_taken

        if not len(rel)>1: continue

        KeyTerms[term] = rel

        # i am not generating json format
        if 0:
            jsonTextRelTerms = ''
            for idx, t in enumerate(rel):
                df = TermCount.get(t, 1)
                jsonTextRelTerms += TmplRelTerm%(t, idx+1, df)
            jsonText += TmplTerm%(term, TermCount.get(term, 1), 1, jsonTextRelTerms)
            #raw_input()

        if 0:
            print "original:", term, " --> ", related
            print "selected:", term, " --> ", rel

        line = "%s -> {%s}"%(term,'; '.join(rel))
        #writefile(File2GramDot, line)
        #print "write line"
        #print line
        #raw_input('...')
    jsonText += "}"
    print jsonText

print "KeyTerm size", len(KeyTerms)

for x in KeyTerms:
    print x
    print KeyTerms[x]
raw_input('...')

TwoGramFileDot = "TwoGram2Term.dot"

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

for tg, terms in TwoGram2Term.items()[:200]:
    if len(terms)>3:
        termquoted = set(['"%s"'%t for t in terms])
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

writefile(TwoGramFileDot, "}")

{
  "TERM-X": {
    "weight": "SCALER",
    "type": 'SCALER',
    "relatedTerms": [
      {
        "name": "TERM-Y",
        "relatedness": "SCALER",
        "weight": "SCALER",
      },
    ]
  },
  "thermal": {
    "weight": 4
  }
}

