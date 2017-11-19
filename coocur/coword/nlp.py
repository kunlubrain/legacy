def sentences():
    # serialize a sequence of sentence

    for idx, (datafile, text) in enumerate(loopWikiData()):

        sentences = cleaner.getSentences(text)
        for s in sentences:
            yield(s)

def termsOfBatch():
    # terms: default to uni-gram
    # batch: size of a text unit or block to analyse, default to sentence
    for s in sentences():
        print s
        raw_input()
