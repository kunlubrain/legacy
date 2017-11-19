# GIVEN:
#     <TITLE>      [TERMS]
#     <ABSTRACT>   [TERMS]
#
# FIND:
#     TERM ---> SCORE
def scoringGram(term, termsTitl, termsAbst):

    s = domainSpecificity(term)
    i = globalConditionalInformation(term, termsTitl)

    w = localWeight(term)

    score = s * i * w

    # for each word
    # sum = for scoringWord(w)


# INFORMATION of a TERM given the TERMS in TITLE
def globalConditionalInformation(term, termsTitl):

    # explore the R-graph and score according to the posterior probability
    for ta in termsAbst:
        for tt in termsTitl:
            # information about ta given tt
            titleInformation += shannon(ta, tt)

def localWeight(term):

    l = len(term.split()) # number of words in term
    nt = termsTitl[term]  # number of occurrence in title terms
    na = termsAbst[term]  # number of occurrence in abstr terms

    weight = l * nt * na  # l**na

def domainSpecificity(term):
    dfTitPmed  = getDF(term, '_PUBMED_', 'TITL')
    dfAbsPmed  = getDF(term, '_PUBMED_', 'ABST')

    # DF in THIS-Domain
    dfThis     = dfAbsPmed

    dfWiki     = getDF(term, '_WIKI_')
    dfIeee     = getDF(term, '_IEEE_')
    dfNews     = getDF(term, '_NEWS_')

    # scoring formula
    crossSpecificity0 = dfThis/dfWiki
    crossSpecificity1 = dfThis/dfIeee
    crossSpecificity2 = dfThis/dfNews

    # domainSpecificity = crossSpecificity0 + crossSpecificity1 + crossSpecificity2
    domainSpecificity = log(crossSpecificity0) + log(crossSpecificity1) + log(crossSpecificity2)

    # condition of significe
    # dfThis > dfNeutral > dfCross


# for gram (w1 w2 w3 w4 w5 w6 w7 w8 w9), if w4 is a verb
def splitbyverb(gram):
    words = gram.split()
    l = len(words)

    indexv = []
    for idx, w in enumerate(words):
        if couldBeVerb(w):
            if not adjective(previousword) and \
               not determinor(previousword):
               # also: w is not in its -ing or -ed (or 3rd sing.?) form
            indexv.append(idx)


"impulse responses exhibiting high sparseness"
"monte Carlo simulations show::3"

    if len(indexv)==0:
        split = False

    if len(indexv)==1:
        gram_left = words[0:indexv[0]]
        gram_right = words[(indexv[0]+1):-1]

        # test
        test1 = DF(gram_left) > thresholdx
        test2 = DF(gram_right) > thresholdy:
        split = test1 and test2:

    if split:
        return gram_left, gram_right

# find the ending subgram which is not proceeded by an adj
def deadjheading(gram):
    words = gram.split()
    l     = len(words)
    for idx, w in enumerate(words):
        if not adjective(words[idx]):
            break

    if not idx==0:
        subgram = words[idx:]

        test1 = DF(subgram) > thresholdx
        test2 = (l - idx) > 2
        if test1 and test2:
            return subgram

def subgram():
    # cascading way
    testgram2 = words[-2:l]
    if DF(testgram2)>threshold:
        testgram3 = words[-3:l]
        if DF(testgram3)>threshold:
            testgram4 = words[-4:l]
            if DF(testgram4)>threshold:
                testgram5 = words[-5:l]
                if DF(testgram5)>threshold:
                    return testgram5
                else:
                    return testgram4
            else:
                return testgram3
        else:
            return testgram2
    else:
        return gram

def droplastverb(gram):
    words = gram.split()
    lastword = words[-1]


    if hardverb(lastword):
        droplast = True

    if softverb(lastword):

        if not adjective(word[-2]):

            if infinite(lastword):

                gram_test = ' '.join(words[0:-1])
                if DF(gram_test) > DF(gram):

                    droplast = True

            if doingForm(lastword):

                if nexttoken in Determinor + Punctuation + :

                    droplast = True

            if doneForm(lastword):

                    droplast = True

    if droplast:
        use the term but not the last word
