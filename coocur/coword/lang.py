import re

import langVocab    as voc
import langLookBA   as lk
import stat

__HARD_STOPS__   = voc.getHardstops()
__SRS__          = voc.getSelfRejectingStops()

__PUNCTURATION__ = voc.getPunctuations()

__ADVERBS__      = voc.getAdvAll()
__ADJECTIVES__   = voc.getAdjAll()
__VERBS__        = voc.getVerbAll()
__VERBS__.update(voc.getVerbNoise())
__VERBS_ED__     = voc.getVerbed()
__VERBS_IRR_ED__ = voc.getIrregularVerbed()
__VERBS_ING__    = voc.getVerbing()
__VERBS_NOUN__   = voc.getVerbNounable()
__VERBS_SING__   = voc.getVerbSingular()
__DETERMINERS__  = voc.getDeterminors()
__WORD2POS__     = voc.readWord2Pos()

def isGeneralDeterminor(word):
    return word in voc.getDeterminors()

def getPosByLookup(word):
    pos = __WORD2POS__.get(word, None)
    if pos: return pos
    if '-' in word: return 'Adj'
    if isPuncturation(word): return 'Punc'
    return 'X'

print "lang.py: word2pos size=", len(__WORD2POS__)

def __splitPuncturation(matchObj):
    return matchObj.group(1) + ' ' + matchObj.group(2)

def __lower(mo): return mo.group(0).lower()

#GIVEN a sentence as a string
#DO change the first letter, if not in acronym, in lower case
def __decaptalizing(s):

    s = re.sub(r'^[A-Z](?=[a-z\b]+)', __lower, s.strip())
    return re.sub(r'^A(?=\s)', __lower, s)

# "MARKER: Blabla ..." -> "Blabla ..."
def __demarking(s):
    return re.sub(r'^[A-Z]+:\s+', '', s.strip())

def isHardStop(word):      return word in __HARD_STOPS__

def isPuncturation(word):  return word in __PUNCTURATION__

def noneWord(word):        return re.search(r'\W', w, re.UNICODE)

def isSRS(word):           return word in __SRS__

def isAdverb(word):        return word in __ADVERBS__

def isVerb(word):          return word in __VERBS__

def isDeterminer(word):    return word in __DETERMINERS__

def isVerbed(word):
    if word in __VERBS_IRR_ED__: return True
    if word.endswith('ed'):
        return word in __VERBS_ED__
    return False

def isAdjective(word):
    return word in __ADJECTIVES__ or isVerbed(word)

def isAdjectiveComparative(word):
    isAdjectiveMutant(word, 'er', voc.getIrregularAdjComparatives())

def isAdjectiveSupalative(word):
    isAdjectiveMutant(word, 'est', voc.getIrregularAdjComparatives())

def isAdjectiveMutant(word, ending, checklist):

    if word in checklist: return True

    if not word.endswith(ending): return False

    endingLen = len(ending)
    try:
        checkword = ''.join(word[:endingLen])
        if isAdjectiveRelative(checkword):
            return True

        # for cases like 'hotter', 'bigger'
        if word[-(endingLen+2)]==word[-(endingLen+1)] and not word[-(endingLen+1)] in voc.getVowels():
            checkword = ''.join(word[:-(endingLen+1)])
            if isAdjectiveRelative(checkword):
                return True

        # for cases like 'busier'
        if word.endswith('i%s'%ending) and not word[-(endingLen+1)] in voc.getVowels():
            checkword = ''.join(word[:-endingLen]) + 'y'
            if isAdjectiveRelative(checkword):
                return True

        return False

    except:
        return False

def isVerbing(word):
    if not len(word)>3: return False
    if not word[-3:]=='ing': return False
    if not word in __VERBS_ING__: return False

def isVerbNoun(word):
    return word in __VERBS_NOUN__

def isVerbSing(word):
    return word in __VERBS_SING__

def isAuxVerb(word):
    return word in voc.getAuxVerb()

def isNumber(word):
    return re.match(r'^\d+$', word)

def isProposition(word):
    return word in voc.getProposition()

def isNonword(word):
    return re.search(r'\W', word, re.UNICODE)

def isNoise(word):
    # ignore if containing non-alphanumeric
    # ignore if pure numbers
    return word in __HARD_STOPS__ or \
        word in __PUNCTURATION__ or \
        re.search(r'[^\w-]', word, re.UNICODE) != None or \
        re.match(r'\d+', word) != None

# GIVEN a SENTENCE as a STRING
# RETURN a LIST-OF-STRING of WORD and PUNCTUATION
def tokenize(sentence):

    # replace WORD, as WORD ,
    # replace WORD: as WORD :
    # replace WORD; as WORD ;
    # replace WORD) as WORD )
    s = re.sub(r'(\w)([,:;\)])(?=\s)',  __splitPuncturation, sentence)

    # replace FOO's as FOO 's
    s = re.sub("(\w)('s)(?=\s)", __splitPuncturation, s)

    # replace WORD" as WORD "
    s = re.sub(r'([\w\.])(")',  __splitPuncturation, s)

    # replace "WORD as  " WORD
    # replace ,WORD as  , WORD
    # replace (WORD as  : WORD
    s = re.sub(r'([,"\(])(\w)',  __splitPuncturation, s)

    #return re.findall('[\w-]+', text)                          # !!! Wonderful
    return re.split('\s+', s)

# GIVEN a TEXT
# RETURN a list of SENTENCES splitted by the S-ENDING PATTERN
def getSentenceList(text):

    # this does not work for '... some number in [0,1]. The ...'
    # sentenceEndingPattern = '(?<=[\w"])\.\s+(?=[A-Z])'
    sentenceEndingPattern = '\.\s+(?=[A-Z])'
    sentences = re.split(sentenceEndingPattern, text)
    sentences = [__decaptalizing(s) for s in sentences]
    sentences = [__demarking(s) for s in sentences]

    return sentences

def getSentences_CleaningForWiki(text):
    def _delimit(m): return '#!*'+m.group(1).strip()
    def _good(s):
        l = len(s.split())
        if l<6: return False
        if l>60: return False
        if not re.search(r'^[A-Z]', s): return False
        return True
    def _lower(m): return m.group(0).lower()
    def _split(m): return '. ' + m.group(1)

    text = re.sub(r'\[[\d\W]+\]', '', text) # remove references like [38]
    text = re.sub(r'\[.{0,30}\]', '', text) # remove references like [by whom?]
    text = re.sub(r'\(.*?\)', '', text) # remove noisy brackets
    text = re.sub(r'".*?"', '', text) # remove noisy quotations
    text = re.sub(r'([A-Z]\.\s*)+', 'X', text) # remove acronym of person's name
    text = re.sub('(?<=[a-z])([A-Z])(?=[a-z])', _split, text) # handle 'fooBar is a ...'

    text = re.sub('\.+\s+([A-Z])', _delimit, text) # standard pattern: word. A-Z
    text = re.sub('(?<=[\w\s])\.+([A-Z])', _delimit, text) # missing space: word.A-Z
    text = re.sub('\s*:\s*([A-Z])', _delimit, text) # break at the column

    sentences = text.split('#!*')
    sentences = [re.sub('^(\w+)', _lower, s) for s in sentences if _good(s)]

    return sentences

def regularwords(tokenlist):
    words = []
    for t in tokenlist:
        if re.search('[A-Z]', t): continue
        if re.search('\d', t): continue
        if re.search('\W', t, re.UNICODE): continue
        words.append(t)
    return words

def markRawPos(tokenlist):
    print tokenlist
    token2pos = []
    for t in tokenlist:
        if isNoise(t):
            token2pos.append((t, 'Z'))
        else:
            pos = __WORD2POS__.get(t, 'X')
            if pos and len(pos)==1 and pos!='X':
                token2pos.append((t, pos))
            elif pos and pos=='X':
                if '-' in t:
                    token2pos.append((t, ['Adj-']))
                else:
                    token2pos.append((t, ['X']))
            else:
                token2pos.append((t, pos))
    print token2pos

# X STOP => X is STOP IF Noun not in POS(X)
def markStopOnNonending(tokenlist, poslist, tokenstoplist):
    numTokens = len(tokenlist)
    marklist = [(t, False) for t in tokenlist]
    for idx, t in enumerate(tokenlist):
        t, stop = tokenstoplist[idx]
        if not stop and idx<(numTokens-1):
            next_t, next_stop = tokenstoplist[idx+1]
            if next_stop:
                pos = poslist[idx]
                if not 'N' in pos and not 'X' in pos:
                    #print "mark it:", t, pos
                    marklist[idx]=(t, True)

    #for idx, t in enumerate(tokenlist): print t, marklist[idx]
    return marklist

def posLookup(tokenlist):
    return [getPosByLookup(t) for t in tokenlist]

# RETURN: LIST of (TOKEN, VERB_MARKER)
def markVerbs(tokenlist, poslist, verbose=False):
    if verbose: print "markverbs for tokens:", tokenlist
    if verbose: print "markverbs via poslist:", poslist
    hardverbmarkers = []
    for idx, t in enumerate(tokenlist):
        pos = poslist[idx]
        if pos==['V']:
            hardverbmarkers.append((t, True))
        elif pos==['V','V3']:
            hardverbmarkers.append((t, True))
        elif pos==['V3','V']:
            hardverbmarkers.append((t, True))
        else:
            hardverbmarkers.append((t, False))

# 'requires', 'that', 'both', 'sensor', 'and', 'fuser', 'share', 'an', 'understanding', 'of', 'the', 'quantization', 'rule'
# 'both', 'quantizer', 'and', 'fuser', 'are', 'working', 'with', 'only', 'partial', 'information', ';', 'if', 'measureme
# ['the', 'thetas-D', 'technique', 'yields', 'suboptimal', 'solutions', 'to', 'nonlinear', 'optimal', 'control', 'problems', 'in', 'the', 'sense', 'that', 'it', 'provides', 'an', 'approximate', 'solution', 'to', 'the', 'Hamilton-Jacobi-Bellman', '(', 'HJB', ')', 'equation']
#
# Special case of Ambiguity:
# power electronic adjustable speed drive controlled electric motor offers superior economics:
#
# fast multipath fading severely degrades average bit error rate performance
# Chinese hamster ovarian cells expressing influenza A virus protein
# network protection transmission line protection relay input sources rotating machinery protection
#
# via
# following desirable features
# difficulty in deciding whether to consider 'X-ing' as a Noun or V-ing:
# asynchronous direct sequence code division multiple access system operating over ... channels
# need some prior knowledge to decide?:
# low cost instrumentation grade FM tape recording system
# dates back ...:
# existing international VHF maritime mobile communication system dates back
#
# This paper presents a general discussion on the control of widely tunable super structure grating distributed Bragg reflector (SSG-DBR) lasers.
#
# prototype boost converter converting universal ac input voltage : 2
# ac input voltage : 4
# carrying one ...
# newly developed high-speed digital time switch LSI makes possible time division switching services
# newly developed high-speed digital time switch LSI makes possible time division switching services

#   by V-ing the

    for idx, t in enumerate(tokenlist):
        try: candidate = t[-3:]=='ing'
        except: candidate = False
        pos, length = poslist[idx], len(tokenlist)
        if candidate:
            if 'Vg' in pos:
                if idx<(length-1):
                    if tokenlist[idx+1] in ['the', 'a', 'an', 'this', 'those', 'these', 'its']:
                        hardverbmarkers[idx] = (t, 'Vg')

        if 'Vg' in pos or 'V' in pos or 'V3' in pos or 'Vd' in pos or 'Vp' in pos:
            try:    leftIsAdv = 'Adv' in poslist[idx-1]
            except: leftIsAdv = False
            try:    rightIsAdv = 'Adv' in poslist[idx+1]
            except: rightIsAdv = False
            if leftIsAdv or rightIsAdv:
                hardverbmarkers[idx] = (t, 'V')

    for idx, t in enumerate(tokenlist):
        if t in ['is', 'are', 'be', 'was', 'were', 'become', 'becomes', 'became']:
            expecting = 'Vd'
            for idx2, tt in enumerate(tokenlist[idx+1:]):
                indexOfToken = idx+1+idx2
                pos = poslist[indexOfToken]
                if 'Adv' in pos: continue
                elif 'Vd' in pos:
                        # expectation confirmed
                        hardverbmarkers[indexOfToken] = (tt, 'Vd')
                        if verbose:
                            print "*** Expectation satisfied:", tokenlist[idx:indexOfToken+1]
                        break
                else:
                        if verbose:
                            print "!!! Expectation of a V-ed denied!"
                            print "marker=", t
                            print "token =", tt
                            print "pos   =", pos
                            print "sequ  =", tokenlist[idx:indexOfToken+1]
                        #break out the expectation sequence
                        break

    if verbose: print "markverbs results:", hardverbmarkers
    return hardverbmarkers

#GIVEN: [(TOKEN, STOP)], [(TOKEN, MARKER)]
#DO: Reset STOP where the MARKER is set to TRUE
def redoStops(tokenstoplist, tokenmarkerlist):
    tokenstops = []
    for idx, tokenstoppair in enumerate(tokenstoplist):
        token1, stop = tokenstoppair
        token2, marker = tokenmarkerlist[idx]
        assert token1==token2
        if marker:
            tokenstops.append((tokenstoppair[0], True))     # set True as a new stop
        else:
            tokenstops.append(tokenstoppair) # use original stop
    return tokenstops

#GIVEN: a LIST of TOKENS
#RETURN: a LIST of (TOKEN, STOP_MARKER), where STOP_MARKER is True or False
#
def markStops(tokenlist):

    hardstopmarkers = []

    for idx, t in enumerate(tokenlist):

        if isNoise(t):
            hardstopmarkers.append((t, True))
            continue

        # look ahead
        if t in lk.LA_STOP:
            if idx<(len(tokenlist)-1):
                signalword = tokenlist[idx+1]
                checklist  = lk.LA_STOP[t]
                if signalword in checklist:
                    hardstopmarkers.append((t, True))
                    continue

        # look behind
        if t in lk.LB_STOP:
            if idx>0:
                signalword = tokenlist[idx-1]
                checklist  = lk.LB_STOP[t]
                if signalword in checklist:
                    hardstopmarkers.append((t, True))
                    continue

        # all above checks fail:
        hardstopmarkers.append((t, False))

    return hardstopmarkers

# GIVEN: a LIST of (TOKEN, STOP_MARKER)
# RETURN: [(ngram, idx1, idx2)] a LIST of NGrams deliminated by the STOPMARKS
#         where the idx1 and idx2 = indexes of the first/last token
def ngrambounds(tslist):
    ngramlist = []
    currentgram = ''
    idxfirstgram = 0
    for idx, ts in enumerate(tslist):
        (token, stopmarker) = ts
        if stopmarker:
            if currentgram!='':
                # push it into the list and reset
                entry = (currentgram.strip(), idxfirstgram, idx-1)
                ngramlist.append(entry)
                currentgram = ''
        else:
            if currentgram=='':
                idxfirstgram = idx
            currentgram += token + ' '
    # consider the ending
    if currentgram!='' and idx>1:
        ngramlist.append((currentgram.strip(), idxfirstgram, idx))

    return ngramlist

# GIVEN: a LIST of (TOKEN, STOP_MARKER)
# FIND: a LIST of TERMS determined by the DETERMINORS
# $tslist : tokenlist with stopmarker
def findDeterminee(tslist):
    pass

def ngramsOfWordlist(wordlist):
    words = ['# ' if isStopWord(w) else w+' ' for w in wordlist]
    ngrams = [n.strip() for n in re.split('# ', ''.join(words)) if n]
    return ngrams

def filterSRS(ngblist, tslist):
    selected = []
    for (ng, idx1, idx2) in ngblist:
        #print ng, idx1, idx2
        if len(ng.split())==1:
            if isSRS(ng):
                #print "   ----- reject!!!"
                continue
        selected.append((ng, idx1, idx2))
    return selected

# REMOVE bad ADJECTIVES
def filterAdj(ngblist, s, verbose=False):
    selected = []
    # pealing backwards
    for (ng, idx1, idx2) in ngblist:
        words = ng.split()
        lastword = words[-1]
        if isAdjective(lastword):
            if len(words)>1:
                newword = ' '.join(words[:-1])
                selected.append((newword, idx1, idx2-1))
            if verbose:
                print "\n\n  ####### adj ending", ng, '\n\n'
        else:
            selected.append((ng, idx1, idx2))
    return selected

#firstly
#tuning ..ly the ==> adverb implying the one before or after it is a verb
#shows, holds

# REMOVE bad ADVERBS
#
def filterAdv(ngblist, s, verbose=False):
    selected = []
    for (ng, idx1, idx2) in ngblist:
        words = ng.split()
        lastword = words[-1]

        if isAdverb(lastword):
            if verbose:
                print "\n\n  ####### adv ending", ng, '\n\n'
            if len(words)>1:
                newword = ' '.join(words[:-1])
                selected.append((newword, idx1, idx2-1))
        else:
            selected.append((ng, idx1, idx2))
    return selected

# gstat: gram statistics
def isTermBySemantic(gram, gstat):

    # test = gstat[gram]['_']['sentence-beginning-followed-by-be-word']:

    test =  'is' in gstat[gram]['r']
    test |= 'are' in gstat[gram]['r']
    test |= 'was' in gstat[gram]['r']
    test |= 'were' in gstat[gram]['r']
    test |= 'has' in gstat[gram]['r']
    test |= 'have' in gstat[gram]['r']
    test |= 'can' in gstat[gram]['r']
    test |= 'could' in gstat[gram]['r']

    if test:
        return True

    return False

def lastVerbingIsVerb(gram, lidx, ridx, tokenlist, gstat):

    wordlist = gram.split()
    lg, lt = len(wordlist), len(tokenlist)

    if ridx == (lt-1):
        return False

    nextword = nextword(ridx, tokenlist)
    prevword = prevword(lidx, tokenlist)

    if isPuncturation(nextword):
        return False

    if isDeterminer(nextword):

        # "V-ing the ..." is a verb
        if lidx==0: return True

        # ADJ V-ing the: strange? TODO - check this
        if isAdjective(prevword): return False

        return True

    else:

        if lidx<=(ridx-1):
            testgram = " ".join(tokenlist[ridx-1: ridx+1])
            if isTermBySemantic(testgram):
                return False # not a verb

        if lidx<=(ridx-2):
            testgram = " ".join(tokenlist[ridx-2: ridx+1])
            if isTermBySemantic(testgram):
                return False # not a verb

        if lidx<=(ridx-3):
            testgram = " ".join(tokenlist[ridx-3: ridx+1])
            if isTermBySemantic(testgram):
                return False # not a verb

        return True

def filterVerb(ngblist, s, verbose=False):
    selected = []
    for (ng, idx1, idx2) in ngblist:
        words = ng.split()
        # Rule-1: drop all the hard-verbs
        foundverb=False
        for idx, w in enumerate(words):
            if isVerb(w):
                foundverb=True

                if verbose:
                    print ngblist
                    print "verb:", w, "from gram:", ng, idx1, idx2

                if idx>0:
                    ngleft = (' '.join(words[0:idx]), idx1, idx1+idx-1)
                    selected.append(ngleft)
                    if verbose: print "L:", ngleft

                if idx<len(words)-1:
                    ngright= (' '.join(words[idx+1:]), idx1+idx+1, idx2)
                    selected.append(ngright)
                    if verbose: print "R:", ngright

                if verbose:
                    print "sentence:\n", s
                    raw_input('...verbs...')

        if not foundverb:
            selected.append((ng, idx1, idx2))

        # Rule-1 Verbs can not be used as ATTRIBUTE ?
    return selected

# return the next word after $index in $tokenlist
def nextword(index, tokenlist):
    if index<(len(tokenlist)-1):
        word = tokenlist[index+1]
        if word in __PUNCTURATION__:
            return '>'
        else:
            return word
    return '>'

# return the previous word after $index in $tokenlist
def prevword(index, tokenlist):
    if index>0:
        word = tokenlist[index-1]
        if word in __PUNCTURATION__:
            return '<'
        else:
            return word
    return '<'

# GIVEN "word"
# RETURN "pos of this word"
def pos(word):
    if isPuncturation(word): return 'PU'
    if isAdverb(word):       return 'AV'
    if isVerbed(word):       return 'VED'
    if isVerbing(word):      return 'VING'
    if isVerbNoun(word):     return 'VN'
    if isVerbSing(word):     return 'VS'
    if isAdjective(word):    return 'AJ'
    if isDeterminer(word):   return 'DE'
    if isAuxVerb(word):      return 'VA'
    if isNumber(word):       return 'NU'
    if isProposition(word):  return 'PP'
    if isNonword(word):      return 'SY'

def profilingCode(word):

    if word in voc.getAuxVerbs():       return '#x'
    if word in voc.getModals():         return '#m'
    if word in voc.getDeterminors():    return '#d'
    if word in voc.getQuesta():         return '#w'
    if word in voc.getPrepositions():   return '#p'
    if isAdjective(word):               return '#j'
    if isAdverb(word):                  return '#v'
    if isPuncturation(word):            return '#u'
    return                                     '#e'

def isSubject(leftindex, rightindex, tokenlist):

    if leftindex==0:

        if rightindex==len(tokenlist)-1:
            #print "gram is the whole sentence:", tokenlist
            return False # boundary-check

        # "WORD WORD <AUX-VERB>" is SUBJECT
        if profilingCode(tokenlist[rightindex+1]) in ['#x', '#m']:
            return True
        return False

    if leftindex==1:

        if rightindex==len(tokenlist)-1: return False # boundary-check

        # "<DETERMINOR> WORD WORD <AUX-VERB>" is SUBJECT
        if profilingCode(tokenlist[0])=='#d' and profilingCode(tokenlist[rightindex+1]) in ['#x', '#m']:
            return True
        return False

    return False

def countInList(term, lr, checklist, stats):
    if term in stats:
        if lr in stats[term]:
            count = 0
            for w, c in stats[term][lr].items():
                if w in checklist:
                    count+=c
            return count
        return 0
    return 0

# Guess if a gram is a term
# Test-s  - #.(is subject)
# Test-1a - #.(followed by <BE> words)
# Test-1b - #.(followed by <PUNC>)
# Test-2a - #.(proceeded by <THE> words)
# Test-2b - #.(proceeded by <PUNC> words)
# Test-3  - #.(df)
def isTerm(term, stats):
    nSubj                = countInList(term, '_', ['s'], stats)
    nRightIsAuxverbs     = countInList(term, 'r', voc.getAuxVerbs(), stats)
    nRightIsPunctuations = countInList(term, 'r', voc.getPunctuations(), stats)
    nLeftIsDeterminors   = countInList(term, 'l', voc.getDeterminors(), stats)
    nLeftIsPunctuations  = countInList(term, 'l', voc.getPunctuations(), stats)
    nDF                  = countInList(term, '_', ['_'], stats)
    score = 0
    score += 20*nSubj
    score += 2*nRightIsAuxverbs
    score += 2*nLeftIsDeterminors
    score += nRightIsPunctuations
    score += nLeftIsPunctuations
    print "   > scoring term", term
    print "     - nSubj", nSubj
    print "     - nRightIsAuxverbs      ", nRightIsAuxverbs
    print "     - nRightIsPunctuations  ", nRightIsPunctuations
    print "     - nLeftIsDeterminors    ", nLeftIsDeterminors
    print "     - nLeftIsPunctuations   ", nLeftIsPunctuations
    print "     - nDF                   ", nDF

    if nDF != 0:
        return float(score)/nDF
    return 0

