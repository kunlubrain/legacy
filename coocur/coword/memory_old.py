# -*- coding: utf-8 -*-

def refreshMemory2D(hist, steps):

    memorySize = 200
    attentionThreshold = 30

    for w1 in hist:

        if len(hist[w1])>memorySize:
            if hist[w1][w1]>attentionThreshold:
                threshold = sorted(hist[w1].items(), key=lambda x:x[1])[-memorySize][1]
                for w2, count in hist[w1].items():
                    if count < threshold:
                        hist[w1].pop(w2)
