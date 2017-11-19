# -*- coding: utf-8 -*-

GERMAN_NOUN_SIMPLE = "\s+([a-zäöü]+)\s+([A-ZÄÖÜ][a-zäöü]+)\s+([\wäöü-]*)[:,.\s$]"
GERMAN_NOUN_UNI = "[A-ZÄÖÜ][a-zäöüß]+"
GERMAN_NOUN_UNI = "[A-Z][a-zäöüß]+"

# Xaeg.Besege
# TODO - robust pattern to extract german-uni-gram, to handle Ä,Ö,Ü
