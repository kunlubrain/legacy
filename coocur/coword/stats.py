import fif

__DF_WORD_WIKI__ = fif.readDFAsRatioFromFile('statDFWord_Wiki.txt', indexOfRatio=2)
__DF_WORD_IEEE__ = fif.readDFAsRatioFromFile('statDFWord_Ieee.txt', indexOfRatio=2)

def getDFOfWordAsRatio_Wiki():
    return __DF_WORD_WIKI__

def getDFOfWordAsRatio_Ieee():
    return __DF_WORD_IEEE__
