#
# Given: parsed word list in "dict.txt"
#
# Do: parse this word list and make a map:
#     word --> [types]
#
import re

FileWordList = 'dict.txt'

def word2types():

    w2t = {}

    with open(FileWordList, 'r') as f:
        tex = f.read()

    #tex = tex[:5000]
    print "total tex len",len(tex)

    # get record for each word
    # using a NON-CONSUMING regex
    regexWordRecord = 'W:.*?(?=\nW:)'

    words = re.findall(regexWordRecord, tex, re.DOTALL)

    print "find %s word records"%len(words)

    # find the word and types in each word record
    regexType = '\n\s+T:(\w+)'
    regexWord = 'W:(\w+)'
    for w in words:
        word = re.search(regexWord, w).group(1)
        types = re.findall(regexType, w)
        types = ','.join([t.lower() for t in types])
        #print "WORD =", word, "     --> ", types
        w2t[word] = types

    return w2t

def _saveBy(w2t, thistype):
    with open('dict%s.txt'%thistype, 'w') as f:
        for w, t in w2t.items():
            if re.match('^%s\w*$'%thistype, t):
                f.write(w+':'+t+'\n')

def save(w2t):
    # save each record as
    # WORD : type1 : type2 : type3
    #
    with open('dictWordTypes.txt', 'w') as f:
        for w, t in w2t.items():
            f.write(w+':'+t+'\n')

    # save those that are only 'adjective'
    _saveBy(w2t, 'adjective')
    _saveBy(w2t, 'noun')
    _saveBy(w2t, 'verb')
    _saveBy(w2t, 'adverb')

w2t = word2types()
save(w2t)
