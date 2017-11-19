def histsize_4d(ctf):
    len1, len2, len3, len4 = 0, 0, 0, 0
    for t in ctf:
        len1+=1
        for tt in ctf[t]:
            len2+=1
            for ttt in ctf[t][tt]:
                len3+=1
                len4+=len(ctf[t][tt][ttt])
    return '%d : %d : %d : %d'%(len1, len2, len3, len4)

def histsize_3d(ctf3):
    len1, len2, len3 = 0, 0, 0
    for t in ctf3:
        len1+=1
        for tt in ctf3[t]:
            len2+=1
            len3+=len(ctf3[t][tt])
    return '%d : %d : %d'%(len1, len2, len3)

def histsize_2d(hist):
    return len(hist), sum(len(h1) for k1, h1 in hist.items())
