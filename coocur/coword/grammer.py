import stats
import lang

def crossDomainInformation(gram, DFThis, DFCross):
    words     = gram.split()
    crossInfo = 1
    for w in words:
        df1, df2 = DFThis.get(w, 0), DFCross.get(w, 0)
        if df1==0 and df2==0: continue
        if df1==0: df1=1e-9
        if df2==0: df2=1e-9
        div = df1/df2
        crossInfo *= div if div>1 else 1/div
        print "> ", w, "df1=", df1, "df2=", df2, "div=", div

    print "gram", gram, "[CROSS-INFO]", crossInfo, '\n'

# given the gram hist after 1st round
# re-select in the 2nd round from one long gram its subgram
def subgram(gram, leftindex, rightindex, hist, tokenlist, poslist):

    words = gram.split()
    size  = len(words)
    assert size==(rightindex-leftindex+1)

    if not "exhibited" in words: return []

    DFWordIeee, DFWordWiki = stats.getDFOfWordAsRatio_Ieee(), stats.getDFOfWordAsRatio_Wiki()

    print "\n_____SUBGRAMMING_____", gram, leftindex, rightindex

    score = lang.isTerm(gram, hist)
    print "score of", gram, score
    crossDomainInformation(gram, stats.getDFOfWordAsRatio_Ieee(), stats.getDFOfWordAsRatio_Wiki())

    candidates = gram.split("exhibited")
    candidates = [c.strip() for c in candidates]
    for c in candidates:
        score = lang.isTerm(c, hist)
        print "score of", c, score
        crossDomainInformation(c, DFWordIeee, DFWordWiki)

    raw_input('...')

    if size>4:
      for i in range(size):
          print '(%s, %s)'%(tokenlist[leftindex + i], poslist[leftindex + i])

      try:
        print "df of gram:", hist[gram]['_']['_']
      except:
        print "ERR: gram [%s] not in hist!"%gram

      if size>1:
          subgram = words[-1]
          if subgram in hist:
              print "lastword df:", hist[subgram]['_']['_']
          else:
              print "lastword not in hist"
      if size>2:
          subgram = ' '.join(words[-2:])
          if subgram in hist:
              print "last2word df:", hist[subgram]['_']['_']
          else:
              print "last2word not in hist"
      return gram
    else:
        return []
    # if df of sub-gram > df of gram and nextword of sub-gram in (is, was, ... has, )


    #  # drop the verb
    #  if lastword is 'verb noun':
    #      drop it if:
    #          nextword in tokenlist is determinator
    #          nextword in tokenlist is adjective
    #          df of the gram without the verb is larger than df of with it
    #          and nextword in the hist of the gram without the verb is aux-verb

    #  # split pattern
    #  NOUN1 VERB ADJ NOUN2  -->  NOUN1,  ADJ NOUN2
    #      (ADJ NOUN2 must itself be a term, e.g. large df, followed by BE, proceeded by DETERMINOR)
    #  ADJ ADJ NOUN1 NOUN2   -->  NOUN1 NOUN2

    #  # hard criterior for term
    #  beginning of a sentence and followed by determinor

def localhist(gramlist):

    hist = {}
    hist_1gram = {}
    hist_2gram = {}
    hist_3gram = {}

    for g in gramlist:
        words = g.split()

        # single-word hist
        for w in words:
            hist_1gram[w] += 1

        for i, w in enumerate(words[:-1]):
            g = ' '.join(words[i:i+2])
            hist_2gram[g] += 1

        for i, w in enumerate(words[:-2]):
            g = ' '.join(words[i:i+3])
            hist_2gram[g] += 1

    # filter out those whose count<2 ?


# 'face and space charge accumulation'
#shield layer going essentially nonconductive
#v-N characteristics exhibited longer times
#"has exhibited ..."
#paper allowing individual networks
#stator winding deterioration mechanisms acting (on ...)
#ICC discussion group A4D comparing (the ...)
#(... to) use water tree growth tests(, ...)
#cable makers introduced triple extrusion
#'extruded', 'outer', 'screens'
#so-called
#'complex', 'power', 'drive', 'system', 'application', 'statistical', 'lifetime-prognosiss.'
#nanocomposites regarding electrical tree growth 
#(... as) barriers obstructing electrical tree growth 3 7
#comparing classical insulation resistance measurements 0 4
#(... the) three-phase amplitude relation diagram makes 23 27 (it ...)
#IEC 60587 IEC standard needs 2 6 (several ...)
#high frequency cable shield properties 20 24 (.)
#
