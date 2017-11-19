import pubmed_dbtest as pmed

papers = pmed.PAPERS

def inc(key, dictionary):
    if not key in dictionary: dictionary[key] = 0
    dictionary[key] += 1

def _insert(_dict, key, val):
    if not key in _dict: _dict[key]=[val]
    else: _dict[key].append(val)

def _save(_file, content):
    with open(_file, 'w') as fh: fh.write(content)

# ========================================
# First create ID for AUTHORS and JOURNALS
def makeid(names):
    id2name = dict([(idx, name) for idx, name in enumerate(names)])
    name2id = dict([(n, i) for i, n in id2name.items()])
    return id2name, name2id

j = set([p['journal'] for p in papers])
jid2jname, jname2jid = makeid(j)

a = set(sum([p['author'] for p in papers], []))
aid2aname, aname2aid = makeid(a)

# ========================================
# AUTHOR -> year -> paper count, paper id
AUTHOR_PAPER_PERYEAR = {}
for a in aname2aid.keys(): AUTHOR_PAPER_PERYEAR[a] = {'total':0, 'peryear':{}}
for p in papers:
    pid, year = p['id'], p['year']
    for a in p['author']:
        if not year in AUTHOR_PAPER_PERYEAR[a]['peryear']:
            AUTHOR_PAPER_PERYEAR[a]['peryear'][year] = [1, [pid]]
        else:
            AUTHOR_PAPER_PERYEAR[a]['peryear'][year][0] += 1
            AUTHOR_PAPER_PERYEAR[a]['peryear'][year][1].append(pid)
        AUTHOR_PAPER_PERYEAR[a]['total'] += 1

#for a, count in AUTHOR_PAPER_PERYEAR.items():
#    if count['total']>1: print a, '=>', count

# === CO-AUTHORS =====================================
AUTHOR_COA = {} # AUTHOR -> CO-AUTHOR -> count
AUTHOR_COA_PP = {} # AUTHOR -> CO-AUTHOR -> [paper id]
for a in aname2aid.keys(): AUTHOR_COA[a] = {}
for a in aname2aid.keys(): AUTHOR_COA_PP[a] = {}
for p in papers:
    pid, year = p['id'], p['year']
    authors = p['author']
    for i, a1 in enumerate(authors):
        for j, a2 in enumerate(authors):
            if i==j: continue
            inc(a2, AUTHOR_COA[a1])  # a2 as coauthor for a1
            _insert(AUTHOR_COA_PP[a1], a2, pid)

#print AUTHOR_COA
#for a, coa in AUTHOR_COA.items(): print a, len(coa)

# ===AUTHOR 2 JOURNAL====================================
AUTHOR_JNL= {} # AUTHOR -> journal -> count
AUTHOR_JNL_PP= {} # AUTHOR -> journal -> [papers]
for a in aname2aid.keys(): AUTHOR_JNL[a] = {}
for a in aname2aid.keys(): AUTHOR_JNL_PP[a] = {}
for p in papers:
    pid, year, jnl = p['id'], p['year'], p['journal']
    authors = p['author']
    for a in authors:
        inc(jnl, AUTHOR_JNL[a])
        _insert(AUTHOR_JNL_PP[a], jnl, pid)

#for a in AUTHOR_JNL:
#    if AUTHOR_PAPER_PERYEAR[a]['total'] > 1: print AUTHOR_JNL[a]

# OK M_PAPER         - id, year, title, abstract, journal, journalid, [(author name, author id)], [keyword]
# __ M_PAPER_R       - id, related paper id, related-by-terms, relatedness score
# OK M_JOURNAL       - id, name, impact factor, h5
# OK M_AUTHOR        - id, name, institute name, institute id
# OK M_AUTHOR_PP_Y   - id, paper count, [paper id], year
# __ M_AUTHOR_CA_Y   - id, [co-author id, paper id, count], year
# OK M_AUTHOR_CA_C   - id, [co-author id, count]
# __ M_AUTHOR_J_Y    - id, [journal id, count], year
# OK M_AUTHOR_J_C    - id, [journal id, count]
# __M_INSTITUTE      - id, city, country

x=20000
php = "<?php\ninclude 'mysql_lib.php';\n"
for p in papers[:x]:
    pid, year, jnl, au = p['id'], p['year'], p['journal'], p['author']
    title, sentences = ' '.join(p['title']), [' '.join(s) for s in p['abstract']]
    abstract = '. '.join(sentences)+'.'
    title    = title.replace('"', "'")
    abstract = abstract.replace('"', "'")
    title = title.replace('(', '_[')
    title = title.replace(')', '_]')
    abstract = abstract.replace('(', '_[')
    abstract = abstract.replace(')', '_]')
    alist = '; '.join(au)
    jid = jname2jid[jnl]
    php += "$_title = $link->real_escape_string(\"%s\");\n"%title
    php += "$_abstract = $link->real_escape_string(\"%s\");\n"%abstract
    php += "$_pub = $link->real_escape_string(\"%s\");\n"%jnl
    php += "$_authors = $link->real_escape_string(\"%s\");\n"%alist
    php += "$_kw= $link->real_escape_string(\"NIL\");\n"
    query="INSERT INTO m_paper SET id=%s, year=%s, title='$_title', abstract='$_abstract', pub='$_pub', pubid=%s, alist='$_authors', kw='$_kw'"%(pid, year, jid)
    php += "$sql = \"%s\";\n"%query
    php += "sql_exec($link, $sql);\n"
php += "?>"
_save('mysql_insert_paper.php', php)

php = "<?php\ninclude 'mysql_lib.php';\n"
for i, j in jid2jname.items()[:x]:
    query="INSERT INTO m_pub SET id=%s, name=\"%s\", impact=%s, h5=%s"%(i, j, len(j)%10+1, len(j)%5*3+1)
    php += "$sql = '%s';\n"%query
    php += "sql_exec($link, $sql);\n"
php += "?>"
_save('mysql_insert_pub.php', php)

php = "<?php\ninclude 'mysql_lib.php';\n"
for i, a in aid2aname.items()[:x]:
    php += "$_name = $link->real_escape_string(\"%s\");\n"%a
    query= "INSERT INTO m_author SET id=%s, name='$_name'"%(i)
    php += "$sql = \"%s\";\n"%query
    php += "sql_exec($link, $sql);\n"
php += "?>"
_save('mysql_insert_author.php', php)

php = "<?php\ninclude 'mysql_lib.php';\n"
for a, p in AUTHOR_PAPER_PERYEAR.items()[:x]:
    aid = aname2aid[a]
    for y, c in p['peryear'].items():
        pid = ';'.join(c[1])
        #php += "$_name = $link->real_escape_string(\"%s\");\n"%a
        #query="INSERT INTO m_author_pp_y SET id=%s, name=\"$_name\", year=%s, count=%s, pid=\"%s\""%(aid, y, c[0], pid)
        query="INSERT INTO m_author_pp_y SET id=%s, year=%s, count=%s, pid=\"%s\""%(aid, y, c[0], pid)
        php += "$sql = '%s';\n"%query
        php += "sql_exec($link, $sql);\n"
php += "?>"
_save('mysql_insert_author_pp_y.php', php)

php = "<?php\ninclude 'mysql_lib.php';\n"
for a, coa in AUTHOR_COA.items()[:x]:
    a1id = aname2aid[a]
    for a2, count in coa.items():
        co_papers = ';'.join(AUTHOR_COA_PP[a][a2])
        a2id =  aname2aid[a2]
        query="INSERT INTO m_author_ca_c SET id=%s, ca_id=%s, count=%s, pid=\"%s\""%(a1id, a2id, count, co_papers)
        php += "$sql = '%s';\n"%query
        php += "sql_exec($link, $sql);\n"
php += "?>"
_save('mysql_insert_author_ca_c.php', php)

php = "<?php\ninclude 'mysql_lib.php';\n"
for a, jp in AUTHOR_JNL.items()[:x]:
    aid = aname2aid[a]
    for j, count in jp.items():
        jid = jname2jid[j]
        pp = ';'.join(AUTHOR_JNL_PP[a][j])
        query="INSERT INTO m_author_pub_c SET id=%s, pubid=%s, count=%s, pid=\"%s\""%(aid, jid, count, pp)
        php += "$sql = '%s';\n"%query
        php += "sql_exec($link, $sql);\n"
php += "?>"
_save('mysql_insert_author_pub_c.php', php)
