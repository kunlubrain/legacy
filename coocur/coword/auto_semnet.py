import re
import os

if 0:
    seed='calcium'
    fname='tmp.txt'
    fname='tmp_calc.txt'
    fieldDelimiter=' '
    SourceWords, SinkWords = set([]), set([])
    with open(fname, 'r') as f:
        for line in f:
            fields = line.strip('\n').split(fieldDelimiter)
            SourceWords.add(fields[0])
            SinkWords.add(fields[1])

    AllWords = SourceWords | SinkWords
    AllWords = SinkWords - SourceWords
    AllWords = [ w.replace('_', ' ') for w in AllWords]
    print AllWords

if 0:
    command='grep "^%s::" ngrams_coocur_10w.txt | cut -d":" -f1,3,5 | tr " " "_" | tr ":" " " | sort -k3 -bgr >> tmp_calc.txt'
    #os.system('rm tmp_calc.txt')
    for w in AllWords:
        os.system(command%w)


if 1:
    fname='tmp_ieee_coocur_selected.txt'
    coocurBook = {}
    with open(fname, 'r') as f:
        for line in f:
            try:
                word1, word2, count = line.strip('\n').split('::')
                coocurBook[word1] = coocurBook.get(word1, {})
                coocurBook[word1][word2] = count
            except:
                print "BAD LINE"
                print line

    # now set
    # 1. a seed word
    # 2. a expansion depth
    maxlen = 0
    for w, hist in coocurBook.items():
        if len(hist)>maxlen:
            seed = w
            maxlen = len(hist)
    print "seed:", seed
    print "maxlen:", maxlen
    seed = "source localization"

    expansionDepth = 1

    # collect all source words
    currentSeeds =  [seed]
    for i in range(expansionDepth):
        newwords = []
        for word in currentSeeds:
            newwords += coocurBook.get(word, {}).keys()
        currentSeeds += newwords
    sourceseeds = set(currentSeeds)
    sourceseeds.remove('IEEE Trans')
    sourceseeds.remove('minimum number')
    print "total #. source seeds", len(sourceseeds)
    print "source seeds", sourceseeds

    # generate the output
    output = "digraph G{\n"
    for s in sourceseeds:
        for sink in coocurBook.get(s, {}).keys():
            sink = sink.strip()

            if sink in ["IEEE Trans", "tens", "nodes", "range sensor"]: continue
            if sink in ["different types"]: continue

            if "good" in sink: continue

            if len(sink)<3: continue
            if re.match('^[a-z]$', sink[0]) and re.search('[A-Z]', sink): continue

            if sink in s: continue
            if s in sink: continue

            #output += ("%s,%s\n"%(s, sink)).replace(' ', '_')
            #s = s.replace('-','_')
            #sink = sink.replace('-','_')
            output += "\"%s\" -> \"%s\"\n"%(s, sink)
    output += "}"

    #write to a file
    print "write to dotfile ..."

    filestem = "tmp_%s"%(seed.replace(' ', '_'))
    dotfile, pdffile = '%s.dot'%filestem, '%s.pdf'%filestem
    with open(dotfile, 'w') as f:
        f.write(output)

    print "generating pdf ..."

    # generate pdf from dotfile
    command='dot %s -Tpdf > %s'%(dotfile, pdffile)
    os.system(command)

    print "saved to file", dotfile, pdffile
