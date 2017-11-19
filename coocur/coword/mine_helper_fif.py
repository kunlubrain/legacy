import re
import io # saving unicode
import codecs # saving unicode


# Global Config
STATS_DIR = 'stats/wiki_de/'

def saveWordFreq(WFHist, totalWordCount, fname):

    filename = 'stats/wiki_de/%s'%fname

    #with open(filename, 'w') as fh:
    with codecs.open(filename, 'w', encoding="utf-8") as fh:

        fh.write('#TOTAL::%d\n'%totalWordCount)

        for k, c in WFHist.items():
            fh.write('%s::%d::%f\n'%(k, c, float(c)/totalWordCount))

    print "word freq saved to", filename

# convert the raw DF to
# 1. remove 'WORD,' as 'WORD'
# 2. replace 'Word' as 'word'
# 3. combine those after above steps
def convertDF(fname, save2file):

    with open(STATS_DIR + fname, 'r') as fh:
        lines = fh.readlines()

    NewDF      = {}
    TotalCount = int(lines[0].split('::')[-1])

    for line in lines[1:]:
        fields = line.strip('\n').replace('::::', '::').replace(':::', '::').split('::')
        if not len(fields)==3: continue
        try:
            word   = unicode(fields[0], 'utf-8').lower()
            word   = re.sub('[,;-]$', '', word)
            dfCnt  = int(fields[1])

            NewDF[word] = NewDF.get(word, 0) + dfCnt

        except:
            print line
            print fields

    print len(NewDF)

    saveWordFreq(NewDF, TotalCount, save2file)

# convertDF('WordDF.txt', 'WordDF_Converted.txt')
