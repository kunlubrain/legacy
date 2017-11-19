# INPUT - a file of networked words based on coocurrence, in form of
#         WORD1 - WORD2 - distance
#
# OUTPU - networks of closely related words, in form of
#         <WORD1, WORD2, WORD3, WORD4>
#
# Criteria
# a group of words are topically related, if the words satisfy:
# any word is a direct neighbour to of them ...  ???

# procedure:
# - start from word x
# - find all neighbours of x, defined as Nx
# - find the union of neighbours of each word in Nx, defined as NNx
# - for each word y in Nx, make a topic group (x,y), total groups defined as Tx
# - at the moment, the number of groups is size(Tx)=size(Nx)
# - for a topic (x, y) in Tx, find the intersect of Nx and Ny, defined as Ixy
# - if Ixy not empty, 
