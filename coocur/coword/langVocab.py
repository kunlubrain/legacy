import re
import langHardStop as stop

__IRR_ADJ_COMPARATIVE__ = {'better':1, 'worse':1, 'less':1, 'more':1, 'further':1, 'farther':1}
__IRR_ADJ_SUPERLATIVE__ = {'best':1, 'worst':1, 'least':1, 'most':1, 'furthest':1, 'farthest':1}

def getHardstops(): return stop.HardStop

def getAuxVerbs(): return stop.AuxVerb
def getModals(): return stop.Modal
def getDeterminors(): return stop.DeterminerGeneral
def getQuesta(): return stop.Questa
def getPrepositions(): return stop.JieCi

def getWordFromFile(filename, wordindex):
 __w = {}
 with open(filename, 'r') as f:
  for line in f:
   fields = line.strip('\n').split()
   if len(fields)==0:  continue
   if fields[0] == '#': continue
   __w[fields[wordindex]]=1
 return __w

def getVowels():
    return ['a', 'i', 'o', 'u', 'e']

def getIrregularAdjComparatives():
    return __IRR_ADJ_COMPARATIVE__

def getIrregularAdjSuperlatives():
    return __IRR_ADJ_SUPERLATIVE__

def getIrregularPlurals():
 __plurals__ = {}
 with open('langNounIrr.txt', 'r') as f:
  for line in f:
   fields = line.strip('\n').split()
   if len(fields)==0:  continue
   if fields[0] == '#': continue
   singular, plural = fields[0], fields[1]
   __plurals__[plural] = singular
 return __plurals__


def getIrregularVerb():
 __i  = {}  # infinite form
 __p  = {}  # simple past
 __pp = {}  # past participle
 with open('langVerbIrr.txt', 'r') as f:
  for line in f:
   fields = line.strip('\n').split()
   if len(fields)==0:  continue
   if fields[0] == '#': continue
   inf, past, pastpart = fields[0], fields[1], fields[2]
   __i[inf] = (past, pastpart)
   __p[past] = inf
   __pp[pastpart] = inf
 return __i, __p, __pp

def getIrregularVerbed():
    virr, vp, vpp = getIrregularVerb()
    return vpp

def getIrregularVerbInOneDict():
    virr, vp, vpp = getIrregularVerb()
    return virr

def getSelfRejectingStops():
    return getWordFromFile('langSRS.txt', 0)

def getAdjZombie():
    return getWordFromFile('langAdjZombie.txt', 0)

def getAdjPure():
    return getWordFromFile('langAdjCollinsPure.txt', 0)

def getAdjExtra():
    return getWordFromFile('langAdjExtra.txt', 0)

def getAdjAll():
    adj = getAdjPure()
    adj.update(getAdjExtra())
    return adj

def getNounNeutral():
    return getWordFromFile('langNounNeutral.txt', 0)

def getAdvPure():
    return getWordFromFile('langAdvCollinsPure.txt', 0)

def getAdvExtra():
    return getWordFromFile('langAdvExtra.txt', 0)

def getAdvAll():
    adv = getAdvPure()
    adv.update(getAdvExtra())
    return adv

def getVerbPure():
    return getWordFromFile('langVerbCollinsPure.txt', 0)

def getVerbInfinitiveAll():
    return getVerbAll()

def getVerbing():
    words = {}
    for i in getVerbInfinitiveAll(): words[presentPerfect(i)] = 1
    return words

def getVerbed():
    words, irregularverbs = {}, getIrregularVerbInOneDict()
    for i in getVerbInfinitiveAll(): words[pastParticiple(i, irregularverbs)] = 1
    return words

def getVerbSingular():
    words = {}
    for i in getVerbInfinitiveAll(): words[singularizes(i)] = 1
    return words

def getVerbAll():
    return getWordFromFile('langVerbCollins.txt', 0)

def getVerbNounable():
    return getWordFromFile('langVerbNounableCollins.txt', 0)

def getVerbAdj():
    return getWordFromFile('langVerbAdjCollins.txt', 0)

def getVerbNoise():
    return getWordFromFile('langVerbNoise.txt', 0)

def getAuxVerb(): return stop.AuxVerb

def getProposition(): return stop.JieCi

def getNonEndingVerbing():
 __v = {}
 __vcond = {} # conditionally non-ending
 with open('langVerbIngNonEnding.txt', 'r') as f:
  for line in f:
   fields = line.strip('\n').split()
   if len(fields)==0:  continue
   if fields[0] == '#': continue
   typ, v = fields[0], fields[1]
   if typ=='n': __v[v]=1
   if typ=='c': __vcond[v]=1
 return __v, __vcond

# GIVEN a verb in its infinitive form
# MAKE its singular form
def singularizes(verb):

    # if ends with 'cdfghklmnprstz' + 'y'
    if verb[-1]=='y' and verb[-2] not in ['a', 'i', 'e', 'o', 'u']:
        return verb[:-1] + 'ies'

    if re.search(r'(ss|x|ch|sh|o)$', verb):
        return verb + 'es'

    return verb + 's'

def presentPerfect(verb):

    __nonvowel = 'b|c|d|f|g|h|j|k|l|m|n|p|q|r|s|t|v |w|x|y|z'

    if re.search('(%s)e$'%__nonvowel, verb):
        return verb[:-1] + 'ing'

    if re.search('(%s)(i|e|o|u)(%s)$'%(__nonvowel, __nonvowel), verb):
        return verb + verb[-1] + 'ing' # double the last character

    return verb + 'ing'

def pastParticiple(verb, irregularverblist):

    if verb in irregularverblist: return irregularverblist[verb][-1]

    if verb.endswith('e'): return verb + 'd'
    return verb + 'ed'

def getDeterminors():
    return stop.DeterminerGeneral

def getPunctuations():
    return stop.Punctuations

def readWord2Pos(fname='Wortebuch.txt'):
    __w = {}
    with open(fname, 'r') as f:
      for line in f:
          fields = line.strip('\n').split('::')
          (word, pos) = fields[0], fields[1]
          __w[fields[0]] = pos.split(',')
    return __w

if __name__=='__main__':
    virr, vp, vpp = getIrregularVerb()
    virrdict  = getIrregularVerbInOneDict()
    nirrp     = getIrregularPlurals()
    vne, vnec = getNonEndingVerbing()
    v         = getVerbInfinitiveAll()
    vpu       = getVerbPure()
    vn        = getVerbNounable()
    vno       = getVerbNoise()
    ving      = getVerbing()
    ved       = getVerbed()
    vs        = getVerbSingular()
    va        = getVerbAdj()

    adj       = getAdjPure()
    adjz      = getAdjZombie()
    adjx      = getAdjExtra()
    adjall    = getAdjAll()

    adv       = getAdvPure()
    advx      = getAdvExtra()
    advall    = getAdvAll()

    nneu      = getNounNeutral()

    srs       = getSelfRejectingStops()

    def take(worddict, n=5):
        return ", ".join(worddict.keys()[:n])

    print "irregular nouns: %s words; first 5:"%len(nirrp), take(nirrp)

    print "irregular verbs - past tense %s; first 5:"%len(vp), take(vp)
    print "irregular verbs - past-participle tense: %s words; first 5:"%len(vpp), take(vpp)

    print "verbs: %s words; first 5:"%len(v), take(v)
    print "verb-ed: %s words; first 5:"%len(ved), take(ved)
    print "verb-ing: %s words; first 5:"%len(ving), take(ving)
    print "verb-3rd: %s words; first 5:"%len(vs), take(vs)
    print "pure-verbs: %s words; first 5:"%len(vpu), take(vpu)
    print "nounable-verbs: %s words; first 5:"%len(vn), take(vn)
    print "adjable-verbs: %s words; first 5:"%len(va), take(va)
    print "verbs-noise: %s words; first 5:"%len(vno), take(vno)

    print "adj: %s words; first 5:"%len(adj), take(adj)
    print "adj zombie: %s words; first 5:"%len(adjz), take(adjz)
    print "adj extra: %s words; first 5:"%len(adjx), take(adjx)
    print "adj all: %s words; first 5:"%len(adjall), take(adjall)

    print "adv: %s words; first 5:"%len(adv), take(adv)
    print "adv extra: %s words; first 5:"%len(advx), take(advx)
    print "adv all: %s words; first 5:"%len(advall), take(advall)

    print "noun neutral: %s words; first 5:"%len(nneu), take(nneu)

    print "self-rejecting stops: %s words; first 5:"%len(srs), take(srs)
