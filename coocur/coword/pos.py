class PosBase:
    def __init(self):
        self.rules = []
        pass

    def addRule(self, r):
        self.rules.append(r)

    def checkRules(self, context):
        for r in self.rules:
            if r.matched(context):
                return True
        return False

class PosNP(PosBase):
    def __init__(self):
        self.addRule()

def posnize_lookup(tokenlist):
    poslist = []
    # add all the possible pos (as candidates)
    for t in tokenlist:
        pos = vocabulary.get(t, 'UNCLASSIFIED')
        poslist.append((t, pos))

# Using the POS-Pattern rules to filter possible POS-candidates
# POS-Pattern Rules
# <the/a/an>     =>  followed-by <ADJ/NOUN>
# <prep>         =>  followed-by <ADJ/NOUN/V-ING>
# <adv>          =>  followed-by <AND/V-ING/V-ED/V-INF/V-3P>
# BEGIN x <be>   =>  x is ADJ* NOUN
# BEGIN x <,>    =>  x is <ADJ* NOUN/ADJ>
# <is>           =>  followed-by ADV* <V-ed>
# <is v-ed to>   =>  followed-by ADV* <V-inf>
# n x-ed prep    =>  x is verb-ed
# n x adj n      =>  x could be verb
# also x-s adj*  =>  x is verb-3p
# as x-ed prep   =>  x is verb
def posnize_checkup(poslist):

