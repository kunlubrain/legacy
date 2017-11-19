def inc(symbol2count, symbol):
    if not symbol in symbol2count:
        symbol2count[symbol]=0
    symbol2count[symbol] += 1

def count(symbollist, symbol2count=None):
    _symbol2count = symbol2count if symbol2count else {}
    for s in symbollist:
        inc(symbol2count, s)
    return _symbol2count

def inc_2d(key1, key2, hist):
    if not key1 in hist: hist[key1]={}
    if not key2 in hist[key1]: hist[key1][key2]=0
    hist[key1][key2]+=1

# count the $symbollist based on $symbol
def count_2d(symbol, symbollist, hist):
    assert type(symbollist)==type([]), "expecting a list, got %s from"%(type(symbollist), symbollist)
    if not symbol in hist: hist[symbol]={}
    for s in symbollist:
        inc(hist[symbol], s)
