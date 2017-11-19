import os

Record2Pos = {}

Query2Record = {}

Query2Pos = {}

POS_TYPE = {}

POS_COMBI = {}

def wordrecords():
  with open('collins.txt', 'r') as f:
      for line in f:
          fields = line.strip('\n').split(':')
          assert len(fields)==3, "bad line > %s"%line

          #     query      record     poslist
          yield(fields[0], fields[1], fields[2].split(';'))


with open('collins.txt', 'r') as f:
    for (word_query, word_record, word_pos) in wordrecords():

        Query2Record[word_query] = Query2Record.get(word_query, [])
        Query2Record[word_query].append(word_record)

        Query2Pos[word_query] = Query2Pos.get(word_query, set([]))
        Query2Pos[word_query] |= set(word_pos)

        Record2Pos[word_record] = Record2Pos.get(word_record, set([]))
        Record2Pos[word_record] |= set(word_pos)


# get all types of POS and combination of POS a word can have
if 0:
  for w, poslist in Record2Pos.items():
      for pos in poslist:
          POS_TYPE[pos]=1
      POS_COMBI[';'.join(poslist)]=1

  for pos in POS_TYPE: print pos
  for pos in POS_COMBI: print pos


if 0:
 HARD_VERB = {}
 with open('tmp4.txt', 'r') as f:
   for line in f:
     fields = line.split()
     count, word = fields[-2], fields[-1]
     pos  = Query2Pos.get(word, ['___'])
     pos  = ';'.join(pos)
     print word, pos
     if pos=='verb':
         print "HARD-VERB:", count, " - ", word

with open('langVerbAdjCollins.txt', 'w') as f:
  for w, poslist in Record2Pos.items():
    if 'verb' in poslist and 'adjective' in poslist:
      f.write(w+'\n')

# find ALL possible verbs
with open('langVerbCollins.txt', 'w') as f:
  for w, poslist in Record2Pos.items():
    if 'verb' in poslist:
      f.write(w+'\n')

# find nounable VERBs
with open('langVerbNounableCollinsPure.txt', 'w') as f:
  for w, poslist in Record2Pos.items():
    if 'verb' in poslist and 'noun' in poslist:
      f.write(w+'\n')

# find pure VERBs
with open('langVerbCollinsPure.txt', 'w') as f:
  for w, poslist in Record2Pos.items():
    if len(list(poslist))==1 and 'verb' in poslist:
      f.write(w+'\n')

# find pure ADJECTIVEs
with open('langAdjCollinsPure.txt', 'w') as f:
  for w, poslist in Record2Pos.items():
    if len(list(poslist))==1 and 'adjective' in poslist:
      f.write(w+'\n')

# find pure ADVERBs
with open('langAdvCollinsPure.txt', 'w') as f:
  for w, poslist in Record2Pos.items()+Query2Pos.items():
    if len(list(poslist))==1 and 'adverb' in poslist:
      f.write(w+'\n')
  for (word_query, word_rec, word_pos) in wordrecords():
    if word_query == word_rec + 'ly':
      f.write(word_query+'\n')


#os.system
