def writeLine2File(text, fname):
    with open(fname, 'a') as fh:
        fh.write(text+'\n')

fname = "pdb/SqlPaper.csv"
savefile = 'pmed_abstract.txt'
with open(fname, 'r') as f:
    for line in f:
        fields = line.split('","')
        abstract = fields[3]
        writeLine2File(abstract, savefile)
        #raw_input("> abs:\n"+abstract)

print "abstract written to", savefile
print "all done"
