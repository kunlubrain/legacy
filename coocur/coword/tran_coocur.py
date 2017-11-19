# transform the coocurrence file into different format, including
# - a csv file used by D3
#

# [INPUT] - the coocurrence file "ngrams_occur_10w.txt"


import fif # for reading and writing files

coocurfile = "stats/wiki_word_coocur.txt"

def trans_csv_on_node(co, w1, max_width):
    # output line format: WORD1::WORD2::CROSS-INFOR 1->2::DF_WORD2
    # output the csv-lines of the network based on $w1
    # calculate cross-information
    #
    h1 = co[w1]
    df_w1 = h1[w1]
    h1.pop(w1) # ignore the self node
    cross_info, cross_info_norm = {}, {}

    for w2, cnt in h1.items():
        df_w2 = co.get(w2, {}).get(w2, 1)
        cross_info[w2] = min(cnt*1.0/df_w2, 1.0)

    # normalize the cross info
    total_info = sum(cross_info.values())
    for w2, cnt in cross_info.items():
        cross_info_norm[w2] = cnt*1.0/total_info

    # write the output
    topx = sorted(cross_info_norm.items(), key=lambda x:x[1], reverse=True)[0:max_width]

    for w2, xinfo in topx:
        df_w2 = co.get(w2, {}).get(w2, 1)
        #                       crossinfor    df_of_word2   total_cross_info
        #print w1, ",", w2, ",", xinfo,        df_w2,        total_info
        line = line_of_d3_link(w1, w2, xinfo, df_w2)
        print line

def trans_csv_all(co):
    for w1 in co.items():
        trans_csv_nodes(co, w1)

def trans_csv_selected(co, selected, max_width):
    for w1 in selected:
        trans_csv_on_node(co, w1, max_width)

def line_of_d3_link(w1, w2, strength, dfword2):
    # {"source":"n1","target":"n2","value":"1.0"}
    template_line = '''{"source":"%s","target":"%s","strength":"%s","targetweight":"%s"},'''
    return template_line%(w1, w2, strength, dfword2)


def expand_network(co, start, max_depth, max_width):
    # go from the $start node in the coocurrence network $co by depth $depth

    def __expand(co, word, max_width):
        new_front = co.get(word, {})
        if len(new_front)>max_width:
            taken = sorted(new_front.items(), key=lambda x:x[1], reverse=True)[0:max_width]
            return [i[0] for i in taken]
        else:
            return new_front.keys()

    depth = 0
    front_nodes = __expand(co, start, max_width)
    visited = [start]
    while depth < max_depth:
        new_front = []
        for new in front_nodes:
            if not new in visited:

                # visit this node
                new_front = new_front + __expand(co, new, max_width)

                # after the visit
                visited.append(new)

        # finish one depth
        depth += 1
        front_nodes = new_front # update the front

        # logging
        print "depth", depth, "new front", set(front_nodes)

    # final result: all found nodes
    return set(visited)

if __name__=='__main__':
    #
    #print "nodes", nodes
    #print "#. nodes", len(nodes)

    hist_coocur = fif.readWordCoocur(coocurfile)
    selected = expand_network(hist_coocur, "red", max_depth=12, max_width=5)
    # trans_csv_selected(hist_coocur, ["red"])
    trans_csv_selected(hist_coocur, selected, max_width=5)
