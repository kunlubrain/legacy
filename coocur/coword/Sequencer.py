import lang

class Sequence:
    def __init__(self, symbollist):
        self.symbollist = symbollist
        self.count = 1

    def has(self, symbol):
        return symbol in self.symbollist

    def indexOf(self, symbol, beginAtIndex=0):
        for i, s in enumerate(self.symbols()[beginAtIndex:]):
            if s==symbol: return beginAtIndex+i
        return -1

    def symbols(self):
        return self.symbollist

    def symbolOfIndex(self, index):
        return self.symbols()[index]

    def size(self): return len(self.symbols())

    def verbose(self): return ' '.join(self.symbols())
    def text(self): return self.verbose()

    def head(self): return self.symbols()[0]

    def inc(self): self.count += 1
    def occurrenceCount(self): return self.count

def compare(seq1, seq2):
    print "comaring ..."
    print "1)", seq1.verbose()
    print "2)", seq2.verbose()

    for i, s in enumerate(seq2.symbols()):
        if i>= seq2.size()-1: break
        if lang.isNoise(s): continue
        idx = seq1.indexOf(s)
        if not idx==-1:
            # find the common part that postceed "$s" in both sequences
            commonpart = []
            lastIndexOfSeq1 = idx
            lastIndexOfSeq2 = i
            filling = None
            for j in range(seq2.size()-i):
                testsymbol = seq2.symbolOfIndex(lastIndexOfSeq2+j)
                crossindex = seq1.indexOf(testsymbol, lastIndexOfSeq1)
                if not crossindex==-1:
                    # new common symbol
                    commonsymbol = testsymbol
                    lastIndexOfSeq1 = crossindex
                    if filling: commonpart.append(filling)
                    commonpart.append(commonsymbol)
                    filling = None
                else:
                    filling = 'FOO'

            if not 'FOO' in commonpart: continue

            print "common part"
            print commonpart

            commonSeq = Sequence(commonpart)
            seqText   = commonSeq.text()
            if seqText in Patterns:
                Patterns[seqText].inc()
            else:
                Patterns[seqText] = commonSeq

Patterns = {}
TextMemory = {}

def learn():
    sentence = "a bc c d fefe gh i jgk ml"
    s = sentence
    words = s.split()
    seq = Sequence(words)
    Patterns[seq.text()] = seq
    newwords = "w ck a bc c x.d hgh i jgk ml".split()
    newseq = Sequence(newwords)

    compare(seq, newseq)
#learn()

def blindMemorize(symbollist):
    seq = Sequence(symbollist)
    TextMemory[seq.text()] = seq

def learnNewSequence(symbolist):
    seq = Sequence(symbolist)
    for text, existingSeq in TextMemory.items():
        compare(existingSeq, seq)

#newseq = "w ck a bc c x.d hgh i jgk ml".split()
#learnNewSequence(newseq)

def showPatterns():
    print "***********  PATTERNS  ***********"
    for text, seq in Patterns.items():
        print text, seq.occurrenceCount()

#showPatterns()
