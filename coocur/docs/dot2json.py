import re

def dot2json(dotfile, jsonfile):

    patternDotLine = r'(".*").*\{(.*)\}'

    with open(dotfile, 'r') as fh:
        text = fh.read()

    lines = re.findall(patternDotLine, text)

    jsonText = "{\n"
    for l in lines:
        term = l[0]
        relatedTerms = ', '.join([r.strip()+':%s'%len(r) for r in l[1].split(';')])
        jsonText += term + ': {' + relatedTerms + '}' + ',\n'
    jsonText = jsonText.strip('\n,') + '\n' "}"

    with open(jsonfile, 'w') as fh:
        fh.write(jsonText)
        print "Saved to", jsonfile

def dot2jsonSimple(dotfile, jsonfile):
    with open(dotfile, 'r') as fh:
        text = fh.read()
    relations = {}
    lines = re.findall("(.*)\s+->\s+(.*)", text)
    for l in lines:
        term = '"%s"'%l[0]
        if not term in relations: relations[term]=[]
        relations[term].append('"%s"'%l[1])
    print relations
    jsonText = "{\n"
    for t, relatedterms in relations.items():
        rt = ', '.join([r+':%s'%len(r) for r in relatedterms])
        jsonText += t + ': {' + rt + '}' + ',\n'
    jsonText = jsonText.strip('\n,') + '\n' "}"

    with open(jsonfile, 'w') as fh:
        fh.write(jsonText)
        print "Saved to", jsonfile


dot2json(dotfile="SemanticNet_IEEE.dot",     jsonfile = "SemanticNet_IEEE.json")
dot2json(dotfile="SemanticNet_PUBMED.dot",   jsonfile = "SemanticNet_PUBMED.json")
dot2jsonSimple(dotfile="SemanticNet_WIKI_Red.dot", jsonfile = "SemanticNet_WIKI_Red.json")
