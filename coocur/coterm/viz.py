# Visualization module
#

def showTerms(terms):
    items = sorted(terms.items(), key=lambda x: x[1])
    for t, cnt in items:
        l = len(t.split())
        if l<2 or l > 4: continue
        if cnt>0:
            print t, " -> ", cnt

def showCD(cd, threshold=0):
    print "\n\n######################################"
    for k, i in cd.items():
        for k2, cnt in i.items():
            if cnt>=threshold:
                print k, " ", k2, "->", cnt

def prof2d_show(p):
    for i, m in p.items():
        #print i, " size:",len(m)
        for j, cnt in m.items():
            if not cnt>0: continue
            print i, "  ", j, "->", cnt

DOT_UD = '''
graph G {
%s
}'''

DOT_DI = '''
digraph G {
%s
}'''

def cd2Dot(p, threshold=2, digraph=True, outputFile='graph_cd'):
    ''' Make a dot graph from a conditional distribution
    '''
    s = ""
    if digraph: g, edge = DOT_DI,  "    %s -> %s [label=%s];\n"
    else:       g, edge = DOT_UD,  "    %s -- %s [label=%s];\n"

    for i, m in p.items():
        for j, cnt in m.items():
            if not cnt>threshold: continue
            s += edge%(i,j,cnt)
    dot = g%s
    print dot
    with open('%s.dot'%outputFile, 'w') as fh: fh.write(dot)
