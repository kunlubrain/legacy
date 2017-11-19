# -*- coding: utf-8 -*-

def refreshMemory2D(hist, steps, prefilter):
    if prefilter:
        for w1, histOfW1 in hist.items():
            if hist[w1][w1] < steps * 0.0003:
                #if hist[w1][w1] < 10:
                    hist.pop(w1)
    for w1 in hist:
        for w2, count in hist[w1].items():
            #if count < hist[w1][w1] * 0.005:
            if count < 0:
                hist[w1].pop(w2)

        memorySize = 200
        if len(hist[w1].items())>memorySize:
            if hist[w1][w1]>30:
                threshold = sorted(hist[w1].items(), key=lambda x:x[1])[-memorySize][1]
                for w2, count in hist[w1].items():
                    if count < threshold:
                        hist[w1].pop(w2)

def refreshMemory2DFirstOrder(hist, steps):
        for w1, histOfW1 in hist.items():
            if hist[w1][w1] < steps * 0.00005:
                if hist[w1][w1] < 10:
                    hist.pop(w1)

# Maintain two records sets:
# 1. Long-Term (Sticky) Record (R1):
#    words -> counts
# 2. Short-Term Memory (R2):
#    words -> counts
# Do an update:
# 1. select form R2 those with large scores
# 2. merge those to R1
# 3. decide to drop some from R1 if capacity overceeded
class Memory:
    def __init__(self):
        self.LTM = {}
        self.STM = {}
        self.capacity = None

    def setInitialCapacity(self, cap):
        self.capacity=cap

    def learnSymbList(self, symbollist):
        for i, s in enumerate(symbollist):
            for ii, ss in enumerate(symbollist):
                self.STM[s] = self.STM.get(s, {})
                self.STM[s][ss] = self.STM[s].get(ss, 0) + 1

    def crosslearn(self, symbolist1, symbolist2, crossweight):
        for s in symbolist1:
            for ss in symbolist2:
                if not ss in symbolist1:
                    self.STM[s][ss] = self.STM[s].get(ss, 0) + crossweight
                if not s in symbolist2:
                    self.STM[ss][s] = self.STM[ss].get(s, 0) + crossweight

    def refresh(self):

        print "refresh memory: STM size=", len(self.STM), "LTM size=", len(self.LTM)

        for s, hist in self.STM.items():
            selfCount = hist[s]
            histSize = len(hist)

            # not worthy converting to LTM
            if selfCount * len(s.split()) < 5:
                continue
            if histSize==1:
                print "> ups: a one-item hist:", hist
                continue

            # select and convert to LTM
            else:
                # 1. select significant/related symbols
                total = sum([hist[ss] for ss in hist if not ss==s])
                num   = histSize-1
                average = total/num
                selected = dict([(ss, cnt) for ss, cnt in hist.items() if hist[ss]>=average])

                if 0:
                    print ">", s
                    print "selected", selected
                    print "from", hist
                    print "average score", average
                    raw_input()

                if not selected or not s in selected:
                    print "fuck:", s
                    print selected
                    print "STRANGE!!! NONE is selected / s not in selected"
                    print s
                    print "average:", average
                    print "select from", hist
                    #raw_input()
                    continue

                # 2. merge the selected to LTM
                self.mergeToLTM(s, selected)

        # reset STM after one refresh
        self.STM = {}

    def showsize(self):
        print "memo LTM size=", len(self.LTM)
        print "memo STM size=", len(self.STM)

    def mergeToLTM(self, s, newHistOnS):
        if not s in self.LTM:
            self.LTM[s] = newHistOnS.copy()
            #print "new item in LTM:", s
            return

        oldHistOnS  = self.LTM[s]
        oldInterval = oldHistOnS[s]
        newInterval = newHistOnS[s]

        # make a temporary hist: g -> (n1, n2)
        tempHist = {}
        for g in oldHistOnS.keys() + newHistOnS.keys():
            tempHist[g] = [oldHistOnS.get(g,0), newHistOnS.get(g,0)]

        if len(tempHist)<self.capacity:
            for g, x in tempHist.items():
                self.LTM[s][g] = x[0] + x[1]
        else:
            # score the symbols and rank by the score
            scoreHist = {}
            for g, x in tempHist.items():

                oldCnt, newCnt = x
                oldCnt = float(oldCnt)
                newCnt = float(newCnt)

                if oldCnt:
                    score = (oldCnt+newCnt)/(oldInterval+newInterval)
                else:
                    if oldInterval>5*newInterval:
                        # got enough history for being sticky
                        score = 0.5 * (newCnt/oldInterval+ newCnt/(oldInterval+newInterval))
                    else:
                        score = (oldCnt+newCnt)/(oldInterval+newInterval)

                scoreHist[g] = [score, oldCnt, newCnt]

            cutoff = sorted(scoreHist.items(), key=lambda x:x[1][0])[-self.capacity][1][0]
            selected = [(ss, x[1]+x[2]) for ss,x in scoreHist.items() if x[0]>=cutoff]

            if oldInterval>5*newInterval and 0:
                print "\n"
                print ">merge for", s, "old size", len(self.LTM[s])
                print ">new hist:", newHistOnS
                print ">old hist:", self.LTM[s]
                print ">new item:", [(i, newHistOnS[i]) for i in newHistOnS if not i in self.LTM[s]]

                print "cutoff:", cutoff
                print "newly added", [(ss,cc,scoreHist[ss][0]) for ss,cc in selected if not ss in self.LTM[s]]
                print "drop old", [(ss,cc,scoreHist[ss][0]) for ss,cc in self.LTM[s].items() if not ss in dict(selected)]
                print oldInterval, newInterval
                print "OLD-SIZE-ON-S", len(self.LTM[s])

            self.LTM[s] = dict(selected)

            if oldInterval>5*newInterval and 0:
                print "NEW-SIZE-ON-S", len(self.LTM[s])
                raw_input()
