# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS
from bs4 import NavigableString
from bs4 import Comment
import urllib
import urllib2
from urlparse import urlparse
from urlparse import urljoin
import mechanize
import re
import timeit
from datetime import datetime
import time


#================
# utilities
#================

#################
### messeging ###
#################
DB_INFO = False
DB_INFO = True

def sinfo(i): print ">", i
def sinfo_go(i): print "\n> [START]", i
def sinfo_ok(i): print "> [DONE] ", i, "\n"
def infoerr(i): print "!!! ERROR:\n", i
def info(i):
    if DB_INFO:
        print "\n********[INFO]%s********"%i

# show a list of info
def info_lst(i, msg="", indent=0):
    if DB_INFO:
        info(msg)
        for x in i:
            print "\t"*indent, x


#################
###    URL    ###
#################

#TestPaperUrl="https://scholar.google.de/scholar?cites=7446088517413169206&as_sdt=2005&sciodt=0,5&hl=en"
TestPaperUrl="https://scholar.google.de/scholar?safe=off&biw=1401&bih=724&bav=on.2,or.r_cp.&bvm=bv.87519884,d.bGQ&sugexp=msedr&gs_rn=62&gs_ri=psy-ab&tok=4UObuBcOJH3zHjhXN15U0w&cp=3&gs_id=1w&xhr=t&um=1&ie=UTF-8&lr&cites=3741462560950630543"
TestWikiUrl="http://en.wikipedia.org/wiki/Python_(programming_language)"
TestJNsTocURL="http://www.jneurosci.org/content/32/1.toc"
TestJNspaperURL="http://www.jneurosci.org/content/32/1/215.full"
URL_AGENT = ["Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11",
             "Mozilla 5.10",
             "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
             "Chrome/35.0.1916.47",
             "Opera/9.25 (Windows NT 5.1; U; en)"]
URL_AGENT_LAST = 0

test_html = r'''
    <body>
    <div class="summarycount">524</div>
    <div class="summarycount">xxx524
    <a href="http://scholoar.google.de/fuckit"></a>
    </div>
    <div class="foo">111</div>
    </body>
'''

def testsoup():
    soup = BS(test_html)
    scores = soup.find_all('div', attrs={'class' : 'summarycount'})
    print type(scores)
    for s in scores:
        print type(s)
        print dir(s)
        print s.attrs
        print s.contents

    # See that 'href' is regarded as an attribute of 'a'
    a = soup.find('a')
    kutils.info("attr of link")
    print a.attrs
    raw_input("quit?")

def get_soup_mechanize(url):
    chrome = mechanize.Browser()
    agent  = URL_AGENT[-1]
    chrome.set_handle_robots(False)
    chrome.addheaders = [('User-agent', agent)]
    base_url = kutils.TestPaperUrl
    #search_url = base_url + keyword.replace(' ', '+')
    search_url = base_url
    page = chrome.open(search_url).read()
    with open("shitgoogle.html", "w") as fh: fh.write(page)
    raw_input("...")
    return BS(page, "lxml")

''' $dummy html is saved test html without the need to urlopen
'''
def get_page(url, logging=True, retry_policy=None):

    # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#5xx_Server_error

    global URL_AGENT_LAST
    agent = URL_AGENT[URL_AGENT_LAST]
    URL_AGENT_LAST = (URL_AGENT_LAST+1)%len(URL_AGENT)       # change the agent
    headers = { 'User-Agent' : agent}
    t = time.time()

    if not retry_policy:
        maxretry = 1
    else:
        maxretry = retry_policy.get('maxretry')

    thistry = 1
    while(thistry <= maxretry):

        #req = urllib2.Request(url)
        req = urllib2.Request(url, None, headers)
        try:
            page = urllib2.urlopen(req, timeout=10)
            return page.read(), 0

        except urllib2.HTTPError as e:

            if e.code in (400, 403, 404):
                print "ERR url  ", url
                print "ERR code ", e.code
                if thistry == maxretry:
                    return None, e.code

            elif e.code in (300, 301, 302, 303, 307):
                try:
                    print "Err code ", e.code, "try again with cookie ..."
                    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
                    page = opener.open(url)
                    return page.read(), 0
                except:
                    if thistry == maxretry:
                        return None, e.code

                # a more complicated solution
                # http://stackoverflow.com/questions/32569934/urlopen-returning-redirect-error-for-valid-links
            else:
                print "ERR url  ", url
                print "ERR code ", e.code
                if thistry == maxretry:
                    return None, e.code

            time.sleep(2*thistry)

        except urllib2.URLError as e:
            print "ERR url  ", url
            print "ERR code ", e.reason
            return None, e.reason
        else:
            msg = io_writable_str(str(e))
            print "ERR url  ", url
            print "ERR code ", msg
            return None, msg

        thistry += 1

    #if logging: sinfo_ok("got url t=%s"%(time.time()-t))
    #with open("shitgoogle.html", "w") as fh: fh.write(page)

def get_soup(url, logging=True, retry=None):
    if logging: sinfo_go("get url %s"%(url))
    page, err = get_page(url, logging, retry)
    soup = BS(page, "lxml") if page else None
    return soup, err

def get_soup_retry(url, minsleep=5, maxretry=5, logging=1):
    retry = {'maxretry':maxretry}
    return get_soup(url, logging, retry)

def get_soup_from_file(fname, logging=False):
    with open(fname, 'r') as fh:
        content = fh.read()
    soup = BS(content, "lxml") if content else None
    return soup

def url_isrelative(url):
    #if re.search('^(www|http|#)', url): return False
    return re.search('^(/|\.\.|index)', url)

def url_ishomo(url, link, logging=False):
    #
    if logging:
        print "url", url
        print "link", link

    if url_isrelative(link):
        if logging:
            print "relative true"
        return True
    if logging:
        print "relative false"

    #
    host1 = urlparse(url).hostname
    host2 = urlparse(link).hostname
    if logging:
        print "host1", host1
        print "host2", host2

    #4
    host1_domain = '.'.join(host1.split('.')[-2:])
    host2_domain = '.'.join(host2.split('.')[-2:])
    #
    # the domain should equal
    if host1 == host2: return True
    #if host1_domain == host2_domain: return True
    return False

def crawl_get_soup(url, minsleep=5, maxretry=5, logging=0):
    try:
        url = url.encode('utf-8')
        return get_soup_retry(url, minsleep, maxretry, logging)
    except:
        return None, "NO-SOUP"

def crawl_clean_soup(soup):
    for x in soup.find_all('script'): x.extract()
    for x in soup.find_all('style'): x.extract()
    for x in soup.find_all('meta'): x.extract()
    for x in soup.find_all('noscript'): x.extract()
    for x in soup.find_all('picture'): x.extract()
    for x in soup.find_all('svg'): x.extract()
    for x in soup.find_all('img'): x.extract()
    for x in soup.find_all('source'): x.extract()
    for x in soup.find_all(text=lambda text:isinstance(text, Comment)): x.extract()
    return soup

def crawl_get_title(soup):
    try:
        return soup.title.string
    except:
        return ''

def crawl_get_links(soup, uniq=True):
    links = [x.get('href') for x in soup.find_all('a') if x.get('href')]
    if uniq:
        return set(links)
    return links

def crawl_get_links_regular(soup, uniq=True):
    links = crawl_get_links(soup, uniq)
    return crawl_select_links_regular(links)

def crawl_get_links_homo(soup, seed):
    links = crawl_get_links_regular(soup)
    links = crawl_select_links_homo(links, seed)
    return [urljoin(seed, l) if url_isrelative(l) else l for l in links]

def crawl_get_body(soup):
    return soup.find('body')

def crawl_get_headers(soup):
    return soup.find_all(['h1','h2','h3','h4'])

def crawl_insert_urltag(soup, url, attag='body'):
    newtag = soup.new_tag('kurl')
    newtag.string = url
    soup.find(attag).insert(0, newtag)
    return soup

def crawl_select_links_homo(links, url):
    return [l for l in links if url_ishomo(url, l)]

def crawl_select_links_startswith(links, prefix):
    pttn = '^'+prefix
    return [l for l in links if l and re.search(pttn, l)]

def crawl_select_links_not_startswith(links, prefix):
    return [l for l in links if not l.startswith(prefix)]

# TODO - check the correctness
def crawl_select_links_regular(links):
    return crawl_select_links_startswith(links, '(www|http|\.\.|index|/)')

def crawl_join_base(seed, links):
    return [urljoin(seed, l) for l in links]

def get_all_links(soup, show=False):
    if show: info("Find all links ...")
    lk_tags = soup.find_all('a')
    for lk in lk_tags:
        if show:
            print lk.text, "herf=", lk.get('href')
    return lk_tags

def filter_links(links, **kargs):
    if 0:
        print "filter links:", links, "args:", kargs
    for name, value in kargs.iteritems():
        if name=='startwith':
            return [l for l in links if l.startswith(value)]
        else:
            assert 0, "Bad args: %s"%name

def tags2text(taglist):
    return [t.text.strip() for t in taglist]

def show_html(TagList):
    for idx, tg in enumerate(TagList):
        print "[item %s] TEXT: "%idx, tg.text

''' print the href in a tag list, with baseurl joined
'''
def show_links(TagList, BaseUrl, Msg=""):
    for idx, tg in enumerate(TagList):
        href = urljoin(BaseUrl, tg.get('href'))
        print "[item %s] "%idx, tg.text, "~", href, "  ", Msg

def urljoinall(urls, baseurl, save2file):
    with open(save2file, 'w') as fh:
        for u in urls:
            fh.write(urljoin(baseurl, u)+'\n')
    print "DONE - joined urls writtenlto", save2file

def pause():
    raw_input("...")

def makeup(s):
    s = s.strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\n',  '', s)
    return s

def prettify(t):
    if type(t)==type([]):
        return [makeup(i) for i in t]
    elif type(t)==type(""):
        return makeup(t)
    elif type(t)==type(u""):
        return makeup(t)
    else:
        print "ERR can not prettify type: ", type(t)
        x=raw_input('print y to show t')
        if x=='y': print t

def purify(t):
    t = t.replace('\r\n',' ').replace('\t',' ').strip()
    t = re.sub('\s+',' ', t)
    return t

def add_urls(filename, urls):
    with open(filename, 'a') as fh:
        for u in urls:
            fh.write(u+'\n')

def save_tocs(tocs):
    with open('js_tocs.txt', 'w') as fh:
        for t in tocs:
            fh.write(t)

def add_tocs(urls):
    add_urls('js_tocs.txt', urls)

def get_toc_urls():
    with open('js_tocs.txt', 'r') as fh:
        t = fh.read().split('\n')
    return t

def add_paper_urls(urls):
    add_urls('js_papers.txt', ["%s %s"%(u[0],u[1]) for u in urls])

''' get all links by matching a given regex for href
    return structure of the links [(href, link text)...]
    urljoin the base url and href
    handling js query with special characters such as &
'''
def get_links_by_regex(soup, base_url, regex, debug=False):
    _links = soup.find_all('a', href=re.compile(regex))
    try: assert(_links)
    except:
        print "no links found with href:%s"%regex
        return []
    _links = [(urljoin(base_url, i.get('href').replace('amp;','')), prettify(i.text)) for i in _links]
    if debug:
        print "> Found links"
        for i in _links: print " ", i
    return _links

''' save $data to a python file named $file_name
'''
def save_py(file_name, data):
    name = file_name + '.py'
    with open(name, 'w') as fh:
        fh.write(data)

def crawl_remove_class(soup, words):
    pttn = '.*%s.*'%'|'.join('(%s)'%w for w in words)
    for w in words:
        pttn = '.*%s.*'%w
        foo = soup.find_all(class_=re.compile(pttn))
        for f in foo: f.extract()
        foo = soup.find_all(id=re.compile(pttn))
        for f in foo: f.extract()
    return soup

def crawl_get_text_bypath(soup, path, lang="en"):
    cont = soup.select(path)
    if cont:
        cont = cont[0].text.strip()
        return io_writable_str(cont)
    else:
        return None

def crawl_get_text_guess(soup, lang='en', logging=False):
    soup = crawl_remove_class(soup, ['footer','hidden'])
    text_content = ''
    #tags = soup.findAll(['div','p'])

    try:
        tags = soup.h1.find_all_next(['div','p'])                  # start after h1
    except:
        tags = soup.body.find_all_next(['div','p'])                  # start after h1

    for t in tags:
        if t.name == 'p':
            this_content = io_writable_str(t.text)
        else:
            ignore =  ['p','style','script','[document]','head']
            ignore += ['button','svg','picture', 'img', 'h1','h2','h3','h4','h5']

            if t.findAll(ignore):
                continue

            if not t.contents:
                if logging: print " > no contents for tag", t
                continue

            if not isinstance(t.contents[0], NavigableString):
                if logging: print " > is not string for tag", t
                continue

            if lang=='en':
                if not len(t.contents[0].split())>10:
                    if logging: print " > content[0] too short", t.contents[0]
                    continue
            elif lang=='ch':
                if not len(re.findall(ur'[\u4e00-\u9fff]', t.contents[0]))>10:
                    if logging:
                        print " > content[0] too short", t.contents[0]
                        print re.findall(ur'[\u4e00-\u9fff]', t.contents[0])
                    continue

            this_content = io_writable_str(t.contents[0])

        if lang=='en':
            if not re.search('[A-Z]', this_content):
                if logging: print " > no A-Z within", this_content
                continue
            if not re.search('\s'   , this_content):
                if logging: print " > no space within", this_content
                continue

        text_content += this_content + '\n'

    if logging:
        print "############### FOUND CONTENT ###############"
        print text_content
    return text_content

def crawl_get_text_regular(soup):

    for x in soup.find_all(text=lambda text:isinstance(text, Comment)): x.extract()

    ignore = ['style', 'script', '[document]', 'head', 'button', 'svg', 'picture', 'img']

    text_content = ''
    for txt in soup.findAll(text=True):

        if txt.parent.name in ignore:
            continue

        txt = re.sub('\s+', ' ', re.sub('\n',' ',txt))

        # filter of irregular text
        # TODO - use score and filter above average
        if not re.search('[,|\.|\?|!]', txt): continue
        if not len(re.findall('\s', txt))>2: continue
        text_content += txt.strip().encode('utf-8') + '\n'
    return text_content

def io_writable_str(s, oneline=True):
    if not type(s) in [type(''), type(u''), type(NavigableString(''))]: return ''
    if oneline: s = re.sub('\n', ' ', s)
    s = re.sub('\s+', ' ', s.strip('\n').strip())
    return s.encode('utf-8')

def get_text(tags, verbose=0):
    textblocks = []
    ignore = ['style', 'script', '[document]', 'head', 'button']
    for t in tags:
        texts = t.findAll(text=True)
        if verbose:
            print "> %d blocks"%len(texts), "from: ", t
        for txt in texts:
            txtstr = txt.strip('\n').strip()
            txtstr = re.sub('\n', ' ', txtstr)
            txtstr = re.sub('\s+', ' ', txtstr)
            if txt.parent.name in ignore:
                continue
            elif re.match('<!--.*-->', txt.encode('utf-8')):
                continue
            elif len(txtstr)<20:
                continue

            if verbose:
                print "> text", txt
            textblocks.append(txtstr)
    return textblocks

def get_text_oneblock(tags, verbose=0):
    texts = get_text(tags, verbose)
    return re.sub('\s+', ' ', ' '.join(texts))

# url agent examples
# http://wolfprojects.altervista.org/articles/change-urllib-user-agent/
# crawl visible text: http://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text

# soup - use CSS for selection:
# http://stackoverflow.com/questions/25745825/python-beautiful-soup-find-particular-heading-output-full-div
# soup.select('div#reportsubsection #subsection'):

# soup - find all use regex
# http://stackoverflow.com/questions/24748445/beautiful-soup-using-regex-to-find-tags
# soup.find_all(['a', 'div']) 
# soup.find_all(re.compile("(a|div)"))

# soup - extract to remove tag
# soup - use isinstance to find tag
# soup - find comment
# http://stackoverflow.com/questions/40529848/python-beautifulsoup-how-to-write-the-output-to-html-file

# urllib2 - http://www.pythonforbeginners.com/python-on-the-web/how-to-use-urllib2-in-python/
# ... it handles authentation, redirection, cookies

# urllib2 - cookie:
# http://stackoverflow.com/questions/4098702/python-urllib2-urlopen-returning-302-error-even-though-page-exists?noredirect=1&lq=1
# urllib2- cookies - redirect: install http_error_3xx handler
# http://stackoverflow.com/questions/8414563/how-to-check-if-the-urllib2-follow-a-redirect

############### error on urllib2 ##############
# ERR url   https://www.nytimes.com/interactive/2017/01/30/podcasts/michael-barbaro-the-daily.html?_r=1
# ERR url   https://myaccount.nytimes.com/mem/tnt.html
# ERR url   https://myaccount.nytimes.com/membercenter/feedback.html
# ERR code  403
# <===  need to sign in
# ERR url   https://topics.nytimes.com/top/reference/timestopics/people/g/doug_glanville/index.html
# <===  connection refused

# urllib2 error code 403
# http://stackoverflow.com/questions/13303449/urllib2-httperror-http-error-403-forbidden
# https://myaccount.nytimes.com/mobile/login/smart/index.html?EXIT_URI=http%253A%252F%252Fmobile.nytimes.com%252F%253FsaveUrl%253Dhttps%25253A%25252F%25252Fwww.nytimes.com%25252Ftips%2526shareID%253Dsharetools-homepage-21-0

# replace tag with its content
# http://stackoverflow.com/questions/1765848/remove-a-tag-using-beautifulsoup-but-keep-its-contents

# visible: selenium visible method; browser automation package
# http://stackoverflow.com/questions/8579383/beautiful-soup-find-elements-having-hidden-style

# URL error: ads
# https://classifieds.wsj.com/ad/Business-For-Sale-Ads
# [Errno 1] _ssl.c:480: error:14077410:SSL routines:SSL23_GET_SERVER_HELLO:sslv3 alert handshake failure

# > http://www.wsj.com/public/page/news-books-best-sellers.html  - found 376 links
# text size 24584
# > http://www.wsj.com/video/browse/news/politics-and-campaign  -  found 90 links
# text size 0

# find chinese character and translate in place:
# http://stackoverflow.com/questions/40122058/python-find-a-series-of-chinese-characters-within-a-string-and-apply-a-function
# find chinese character: using '[\u4e00-\u9fff]+'
# http://stackoverflow.com/questions/2718196/find-all-chinese-text-in-a-string-using-python-and-regex
