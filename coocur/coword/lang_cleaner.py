# -*- coding: utf-8 -*-

import re

# remove [NUMBER], [...]
def removeReferences(text):
    return re.sub('\[[\d,\.]+\]', ' ', text)

def removeQuotations(text):
    text = re.sub(r'".*?"', ' ', text)  # remove noisy quotations
    text = re.sub(r'„.*?“', ' ', text)  # german quotation
    return text

def removeBraces(text):
    return re.sub(r'\(.*?\)', ' ', text) # remove noisy brackets

def removeNonText(text):
    text = removeReferences(text)
    text = removeQuotations(text)
    text = removeBraces(text)
    return text

def replaceJahrhundert(text):
    # im 18. Jahrhundert
    return re.sub('\d+\.\s?(?=Jahr)', '1 ', text)

def replaceUnicodeNonBreakSpace(text):
    return text.replace("\xc2\xa0", " ")

def regularize(text):
    text = replaceJahrhundert(text)
    text = replaceUnicodeNonBreakSpace(text)
    return text

def splitToSentences(text):
    PatternSentDelim =  '\.\s?(?=[A-Z\d])'  # "foo. 1927 entstanden ..."
    PatternSentDelim =  '[\.\?\!][\s\n]+'

    return re.split(PatternSentDelim, text)

def __goodSentence(s, verbose=0):
    sLength       = len(s)
    nonTextChar   = len(re.findall('\W', s))
    nonTextWord   = len([w for w in s.split() if len(w)==1])
    lenLowerWords = len([w for w in s.split() if re.search('^[a-z]', w)])

    if verbose:
        print "> sent check:", s
        print sLength
        print nonTextWord
        print lenLowerWords
        print s.split()

    if sLength<30 or sLength>1000: return False
    if nonTextWord > 5:            return False
    if lenLowerWords < 5:          return False
    return True

def filterSentences(sentList, debug=0):
    if debug:
        for s in sentList:
            if not __goodSentence(s):
                print "BAD SENT:", s
    return [s for s in sentList if __goodSentence(s)]


def getSentences(text):

        text      = removeNonText(text)
        text      = regularize(text)
        sentences = splitToSentences(text)
        sentences = filterSentences(sentences)

        return sentences

def getSentences_regex(text):

    # this does not work for '... some number in [0,1]. The ...'
    # sentenceEndingPattern = '(?<=[\w"])\.\s+(?=[A-Z])'
    sentenceEndingPattern = '\.\s+(?=[A-Z])'
    sentences = re.split(sentenceEndingPattern, text)
    return sentences

def tokenize(sentence, tolower=1):
    #for german the capitalization is useful
    if tolower: sent = unicode(sentence, 'utf-8').lower()
    else:       sent = unicode(sentence, 'utf-8')

    sent = re.sub('[;,":] ', ' , ', sent)
    sent = re.sub('\s+',     ' ', sent)

    return sent.split()

def tokenize_simple(sent):
    sent = unicode(sent, 'utf-8')
    sent = re.sub('[;,":] ', ' , ', sent)
    sent = re.sub('\s+',     ' ', sent)
    return sent.split()

def capitalizedWordsOf(sent):
    return [w.strip() for w in re.findall('(?<=[a-z]\s)\s*[A-Z]\w+', sent)]
# UNICODE Table: http://www.utf8-zeichentabelle.de/unicode-utf8-table.pl?start=128&number=128&utf8=string-literal&unicodeinhtml=hex

