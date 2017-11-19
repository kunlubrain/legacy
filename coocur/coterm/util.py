# GIVEN: a list of terms ['A B C', 'A E', 'C K']
# RETURN: a flat list of single words ['A','B','C','A','E','C','K']
#
def flat(termlist):
    # NOTE assuming ther terms in $termlist are whitespace-striped
    return ' '.join(termlist).split()

def dictsize(_dict):
    keysize = len(_dict)
    valsize, maxvalsize, minvalsize, avesize = 0, 0, 10*6, 0
    for k in _dict:
        try: size = len(_dict[k])
        except: size = 1
        valsize += size
        if size>maxvalsize: maxvalsize=size
        if size<minvalsize: minvalsize=size
    avesize = valsize*1.0/keysize
    return "size %s, total_len %s, max_len %s, min_len %s, ave_len %.3s"%(keysize, valsize, maxvalsize, minvalsize, avesize)

def dictfilter(d, threshold):
    _d = {}
    for k, i in d.items():
        if i>= threshold: _d[k]=i
    return _d
def dictfilter2d_nonempty_inplace(d):
    for k, i in d.items():
        if not i: del d[k]
        #if k=='': del d[k]
def dictfilter2d(d, threshold):
    _d = {}
    for k, dd in d.items():
        for k2, cnt in dd.items():
            if cnt>= threshold:
                if not k in _d: _d[k]={}
                _d[k][k2]=cnt
    return _d
def dictfilter2d_inplace(d, threshold):
    for k, dd in d.items():
        for k2, cnt in dd.items():
            if not cnt>= threshold:
                del d[k][k2]
