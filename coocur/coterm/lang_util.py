
--- find the ACRONYM
    if enclosed in ()
        if len < ...
        if no space
            if begins with A-Z
                ACRO = matched A-Z
                find the name for ACRO
        if with space


    findTextForAcro(ACRO)
        word = previous word


        case - previous words enclosed with ""
        case - two LETTERs in one word (intracranial as IC)
        case - ignore like: some text (Group 1)
        case - ignore (U.S. dollars)

        simple regex:
            num = len(ACRO)
            previous num-words

            regex = WordBound + FIRSTLETTER + \w + SECONDLETTER + \w ...



--- remove single words (nouns):
    frequency-wiki = frequeny of word-i in wikipedia
    frequency-domain = frequency of word-i in this domain jounral
    frequency-ref = frequency of word-i in a neutral domain

    note the 0 handling

    retio = frequency-wiki / frequency-domain


--- word filtering
    if word ends with 'lly' --- ignore


--- city pattern: city + street: Edinburgh EH16 4SB; London W6 8RF
--- sometimes no country, just city: Milwaukee,Wisconsin,WI 53295
---- Mansfield Road,OX1 3QT Oxford


you can search for synnonym:
    https://www.sketchengine.co.uk/


Synonym finding
 - pattern of usage
 - CATEGORY mapping:
    - categories: C={a, b, c, d, ...}
    - noun n
        - map n to ci in C

???????????????????????????????????????????
???????????????????????????????????????????
????                                    ???
???                NEEDS                ???
????                                    ???
???????????????????????????????????????????
???????????????????????????????????????????


relationship mining ?

highlighting
    given:
        terms in title
        terms in abstract
        term frequncy profile
    find:
        the most important sentences
        else?
    do:
        output:
            levels of importance
                high - red, bold
                normal -
                light
                trivial - ignore as null
        seti: terms by length-i
        for s as a sentence
            ts as terms in s
                seti-ts as terms by length-i
                feqi-ts as term frequency for terms in seti-ts


