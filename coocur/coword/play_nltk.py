import nltk
from nltk.tokenize import word_tokenize

with open('tmp.txt', 'r') as f:
    for textline in f:
        sentences = textline.split('. ')
        for s in sentences:
            poslist = nltk.pos_tag(word_tokenize(s))

            print "____________________________"
            print s
            print "pos:"
            print poslist
            raw_input()
