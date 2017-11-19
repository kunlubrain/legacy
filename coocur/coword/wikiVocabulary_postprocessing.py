# find all the mutants of verbs or nouns

# get all the words
V={}
with open('wikiVocabulary.txt','r') as f:
 for l in f:
  fs=l.strip('\n').split('::')
  w,c=fs[0],int(fs[1])
  V[w]=c

# find verbs
VB={}
for w,c in V.items():
  cing, ced, cs = 0, 0, 0
  if w+'ing' in V:        cing =  V[w+'ing']
  if w+w[-1]+'ing' in V:  cing += V[w+w[-1]+'ing']
  if w.endswith('e') and w[:-1]+'ing' in V:  cing += V[w[:-1]+'ing']
  if w+'ed' in V:         ced  += V[w+'ed']
  if w+w[-1]+'ed' in V:   ced  += V[w+w[-1]+'ed']
  if w.endswith('e') and w+'d' in V:         ced  =  V[w+'d']
  if w.endswith('y') and w[:-1]+'ied' in V:  ced  += V[w[:-1]+'ied']
  if w+'s' in V:         cs +=  V[w+'s']
  if w+'es' in V:        cs +=  V[w+'es']
  if w.endswith('y') and w[:-1]+'ies' in V:  cs   += V[w[:-1]+'ies']
  if cing!=0 or ced!=0 or cs!=0:
    cc = c + cing + ced + cs
    VB[w]=cc

# find verbs
VS={}
for w,c in V.items():
  cing, ced, cs = 0, 0, 0
  if w+'s' in V:         cs +=  V[w+'s']
  if w+'es' in V:        cs +=  V[w+'es']
  if w.endswith('y') and w[:-1]+'ies' in V:  cs   += V[w[:-1]+'ies']
  if cing!=0 or ced!=0 or cs!=0:
    cc = c + cing + ced + cs
    VS[w]=cc
