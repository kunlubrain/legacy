import fif
import histsize as histsize

# process the results
# generate dot file

def semantic_summary(fname, threshold, topx, reflexive=True):
    # ctf: w1-w2-count
    # ctf3: w1-w2-w3-count
    # reflexive: allow two nodes pointing to each other

    # to have:
    # w1 - w2 - count - [w3, w4], where w3 and w4 are the top-2 semantic anchors for w1 and w2

    # read in data
    ctf = fif.readCTF3(fname, threshold)
    print "ctf size=", histsize.histsize_3d(ctf)

    # summerize data
    summary = {}
    for w1, h1 in ctf.items():
        for w2, h2 in h1.items():
            total_cnt = sum([int(c) for w3, c in h2.items()])
            anchors = sorted(h2.items(), key=lambda x:int(x[1]), reverse=True)[0:topx]

            if not reflexive:
                if w2 in summary:
                    if w1 in summary[w2]:
                        continue

            if not w1 in summary: summary[w1]={}
            summary[w1][w2] = anchors

    print "summary size ", histsize.histsize_2d(summary)
    return summary

dot_head_tmpl = '''graph g {\n rankdir=LR;\n'''
dot_line_tmpl = '%s -- %s [ label = "%s" ];\n'
dot_tail_tmpl = 'Rot [fillcolor=red, color=orangered, fontsize=30];\n}'

def gen_dot(summary, nodes, dotfile):
    # to dot format
    #w1 - w2 - [label = ""]
    with open(dotfile, 'w') as fh:
        fh.write(dot_head_tmpl)
        nodepairs = []
        for w1 in nodes:
            if not w1 in summary: continue
            for w2, anchors in summary[w1].items():

                # do not add the same edge twice
                tmp_str = '%s:%s'
                if tmp_str%(w1, w2) in nodepairs or tmp_str%(w2, w1) in nodepairs:
                    continue
                l = ':'.join(a[0] for a in anchors)
                dot_line = dot_line_tmpl%(w1, w2, l)
                fh.write(dot_line)

                nodepairs.append(tmp_str%(w1, w2))

        fh.write(dot_tail_tmpl)
    print "[DONE] saved to", dotfile


def select(summary, seed, depth):
    found = [seed]
    front = found
    for i in range(depth):
        newfront = []
        #print "\n", i, "curr front", front
        for s in front:
            #print "  checking", s
            if s in summary:
                newfront += summary[s].keys()
                #print "     > add ", summary[s].keys()
        front = [f for f in  set(newfront) if not f in found]
        found += newfront
        #print "next front", front
    return set(found)

FIN_SEM3 = 'stats/gutefrage/ctf3_gutefrage.txt'
FOUNT_SEM3_DOT = 'stats/gutefrage/semnet_gutefrage_%s.dot'

FIN_SEM3 = 'stats/gutefrage/ctf_mem_sem3.txt'
FOUNT_SEM3_DOT = 'stats/gutefrage/semnet_%s.dot'


#summary = semantic_summary(FIN_SEM3, threshold=10, topx=4)
summary = semantic_summary(FIN_SEM3, threshold=5, topx=4)

seed = 'Rot'
nodes = select(summary, seed, 2)
gen_dot(summary, nodes, FOUNT_SEM3_DOT%seed)
