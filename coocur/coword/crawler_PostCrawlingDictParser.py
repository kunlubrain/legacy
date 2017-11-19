# -*- coding: utf-8 -*-

#--------------------------
# From CrawledSourceFile, get the POS for all WORDS
# and hence construct a Wortebuch from word to pos
# Source file:
# Crawled from dict.cn
# Crawled from collins.com
#--------------------------

Vocab           = {}
Vocab_Clone     = {}
WordsWithoutPos = []

def addPos2Word(word, pos):
    if not word in Vocab: Vocab[word] = [pos]
    else: Vocab[word].append(pos)

def hasPos(pos):
    if not pos:
        print " ! No POS:", line
        WordsWithoutPos.append(searchWord)
        return False
    return True

def lookupPos(pos, word):
    if   p in ['adj.', 'adjective']:  addPos2Word(recordWord, 'Adj')
    elif p in ['comparative adjective']:  addPos2Word(recordWord, 'Adj2')
    elif p in ['superlative adjective']:  addPos2Word(recordWord, 'Adj3')
    elif p in ['n.', 'noun', 'singular noun']:    addPos2Word(recordWord, 'N')
    elif p in ['plural noun']:    addPos2Word(recordWord, 'Np')
    elif p in ['vt.']:   addPos2Word(recordWord, 'V')
    elif p in ['past participle of verb']:   addPos2Word(recordWord, 'Vd')
    elif p in ['past tense of verb']:   addPos2Word(recordWord, 'Vp')
    elif p in ['present participle of verb']:   addPos2Word(recordWord, 'Vg')
    elif p in ['3rd person singular present tense of verb']:   addPos2Word(recordWord, 'V3')
    elif p in ['vi.']:   addPos2Word(recordWord, 'V')
    elif p in ['v.', 'verb']:    addPos2Word(recordWord, 'V')
    elif p in ['int.', 'exclamation']:  addPos2Word(recordWord, 'Int')
    elif p in ['adv.', 'adverb']:  addPos2Word(recordWord, 'Adv')
    elif p in ['abbr.', 'symbol for', 'abbreviation for']: addPos2Word(recordWord, 'Symb')
    elif p in ['modifier']: addPos2Word(recordWord, 'Modi')
    elif p in ['prep.', 'preposition']: addPos2Word(recordWord, 'Prep')
    elif p in ['pron.', 'pronoun']: addPos2Word(recordWord, 'Pron')
    elif p in ['aux.']:  addPos2Word(recordWord, 'Aux')
    elif p in ['pref.', 'prefix']: addPos2Word(recordWord, 'Prefix')
    elif p in ['conj.', 'conjunction']: addPos2Word(recordWord, 'Conj')
    elif p in ['sentence connector']: addPos2Word(recordWord, 'Conj')
    elif p in ['num.', '']:  addPos2Word(recordWord, 'Num')
    elif p in ['art.', '']:  addPos2Word(recordWord, 'Art')
    elif p in ['determiner']:  addPos2Word(recordWord, 'Det')
    elif p in ['def.']:  addPos2Word(recordWord, 'Def')
    elif p in ['suf.', 'suffix']:  addPos2Word(recordWord, 'Sufix')
    elif p in ['sentence substitute']:  addPos2Word(recordWord, 'Subs')
    elif p in ['the internet domain name for']: pass
    elif p in ['unknown']: pass
    else:
        print "unclassified pos:", p
        print "raw line:", line
        raw_input()


if 0:
    fname = 'pos_dict.txt'
    with open(fname, 'r') as f:
        for line in f:
            line = line.strip('\n')
            fields = line.split('::')

            searchWord = fields[0]
            recordWord = fields[1]
            pos        = fields[2]
            if not hasPos(pos): continue

            poslist    = pos.split(',')
            for p in poslist:
                lookupPos(p, word)

            try:    mutants = fields[3]
            except: continue

            mutantlist = mutants.split(',')
            for m in mutantlist:
                (typ, word) = m.split(':')
                if   typ=='形容词':       addPos2Word(word, 'Adj')
                elif typ=='过去式':       addPos2Word(word, 'Vp')
                elif typ=='过去分词':     addPos2Word(word, 'Vd')
                elif typ=='现在分词':     addPos2Word(word, 'Vg')
                elif typ=='第三人称单数': addPos2Word(word, 'V3')
                elif typ=='比较级':       addPos2Word(word, 'Adj2')
                elif typ=='最高级':       addPos2Word(word, 'Adj3')
                elif typ=='名词':         addPos2Word(word, 'N')
                elif typ=='名词复数':     addPos2Word(word, 'Np')
                elif typ=='副词':         addPos2Word(word, 'Adv')
                elif typ=='动词':         addPos2Word(word, 'V')
                elif typ=='简写符号':
                    Vocab_Clone[word]=recordWord
                    addPos2Word(word, 'Symb')
                elif typ=='异体字':
                    if word==recordWord:
                        # actually the same
                        continue
                    Vocab_Clone[word]=recordWord
                    print "Clone:", word, " <-->", recordWord
                else:
                    print "unclassified type:", typ, word
                    print "raw line:", line
                    assert False

# ----------- bad results from dict.cn --------------
# This is incorrect:
# stalinism::stalinism::n.::形容词:Stalinist,动词:Stalinize
# more::more::pron.,adv.

# ----------- Collins --------------
#
if 1:
    fname = 'collins.txt'
    with open(fname, 'r') as f:
        for line in f:
            line = line.strip('\n')
            fields = line.split(':')
            searchWord = fields[0]
            recordWord = fields[1]
            pos        = fields[2]
            if not hasPos(pos): continue

            poslist    = pos.split(';')
            for p in poslist:
                lookupPos(p, recordWord)

# ----------- Now, save the results --------------
if 0:
    with open('Wortebuch_Dictcn.txt', 'w') as f:
        for w, pos in Vocab.items():
            pos = set(pos)
            f.write("%s::%s\n"%(w, ','.join(pos)))

print "ALL DONE"
