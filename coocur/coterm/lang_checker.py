# find out word of interest in a unit e.g. a sentence
import re

PREPOSITION = [ 'for', 'by',

    'with', 'within', 'without',

    'on', 'onto', 'over', 'under', 'at', 'out',

    'in', 'into', 'between', 'among','outside', 'nearby', 'near',

    'of',

    'from', 'to',

    'before', 'after', 'and',

    'or', 'if', 'must', 'not',

    'far', 'here',

    'only', 'because',

    'while', 'whereas', 'always'

    'better',

    'as', 'also',

    'oppose',

    'via',

    'across', 'against', 'throughout', 'toward', 'towards',
    'versus',

    'What', 'When', 'Where', 'Who', 'Why',
    'what', 'when', 'where', 'who', 'why',

    # They are not prepositon, but useful for terms extraction
    'more', 'less', 'How', 'how',
    'getting', 'conveyed', 'II', 'I',
    'new',
    'other', 'further', 'whether', 'been',
    # handle such cases
    #'associated with', 'required for'
    'findings', 'results',
    'none', 'yet',
    'about',
    'along',

    'per',   # TODO, 'per month' is not useful, but 'per XXX' might be?
    'previously',
    'often',
    'both',
    'five', 'six', 'four',
    '',
]

ADJUNCTIVE = [
    'hence', 'therefore', 'thus',
    'following', 'followed', 'during', 'beyond',
    'but', 'although', 'though', 'except',
    'using', 'through',
    'than',
    'suggesting',
    'linking',

    'vivo',

    # adv
    'selectively',
]

MODAL = [ 'may', 'could', 'would', 'should', 'when', 'can',
          'does', 'do',
          'be', 'is', 'are', 'was', 'were',
          'have', 'has', 'had',
        ]

PRONOUN = ['each', 'every', 'any',
           'it', 'we', 'they',
           'most', 'many', 'few', 'all',
           'our',  'their', 'its', 'whose',
           'this', 'that', 'these', 'those',
           'which'
          ]

ARTICLE = ['the', 'a', 'an']

VERBS = ['controls', 'control',
         'reveals', 'reveal',
         'predicts', 'predict',
         'protects', 'protect',
         'potentiates', 'potentiate',
         'increases', 'increase',
         'regulates', 'regulate',
         'induces', 'induce',
         'drives', 'drive',
         'underlies', 'underlie',
         'separates', 'separate',
         'impairs', 'impair',
         'triggers', 'trigger',
         'underlying', 'underlies',
         'reduces', 'reduce',
         'forms', 'form',
         'mediates', 'mediate',
         'facilitate', 'facilitates',
         'instruct',
         'transduces', 'transduce',
         'activates', 'activate',
         'encodes', 'encode',
         'reproduces', 'reproduce',
         'shows', 'show',
         'explains', 'explain',
         'inhibits', 'inhibit',
         'prevents', 'prevent',
         'enhances', 'enhance',
         'receives', 'receive',
         'accelerates', 'accelerate',
         'suppresses', 'suppress',
         'generates', 'generate', 'generated',
         'determines', 'determine',
         'implicates', 'implicate',
         'releases', 'release',
         'reflects', 'reflect',
         'reverses', 'reverse',
         'modulates', 'modulate',
         'influences', 'influence',
         'promotes', 'promote',
         'causes', 'cause',
         'removes', 'remove',
         'tells', 'tell',
         'evokes', 'evoke',
         'improves', 'improve',
         'orchestrates', 'orchestrate',
         'requires', 'require', 'requiring',
         'affects', 'affect',
         'correlates', 'correlate',
         'decorrelates', 'decorrelate',
         'abolishes', 'abolish',
         'synergizes', 'synergize',
         'recruits', 'recruit',
         'resets', 'reset',
         'disrupts', 'disrupt',
         'confers', 'confer',
         'creates', 'create',
         'specifies', 'specify',
         'directs', 'direct',
         'streamlines', 'streamline',
         'modifies', 'modify',
         'decrease', 'decreases',
         'contains', 'contain',
         'uncouples', 'uncouple',
         'alters', 'alter', 'altered'
         'represents', 'represent',
         'remodels', 'remodel',
         'produces', 'produce',
         'provides', 'provide',
         'boosts', 'boost',
         'targets',
         'refines', 'refine',
         'enables', 'enable',
         'contributes', 'contribute',
         'blocks', 'block',
         'involves', 'involve',
         'follows', 'follow',
         'supports', 'support',
         'shapes', 'shape', ### <-- can this generalize
         'restores', 'restore',
         'defines', 'define',
         'illuminates', 'illuminate',
         'propose', 'proposes',
         'found', 'find', 'finds',
        ]

CONNECTORS = PREPOSITION + ADJUNCTIVE + MODAL + PRONOUN + ARTICLE + VERBS


def is_connector(s):
    if s.lower() in CONNECTORS:
        return True
    return False

def can_begin(s):
    test = not is_connector(s)
    return test

def can_end(s):
    test = not is_connector(s)
    return test

def usable(s):
    #test1 = re.match('[0-9a-zA-Z_-]+$', s)
    test1 = re.match('[a-zA-Z\-]+$', s)  # only for dot graph test
    test2 = len(s)>1
    test3 = re.search('[a-zA-Z\-]', s)
    return test1 and test2 and test3

def good(s):
    return usable(s) and can_begin(s)

def isStop(s):
    return s.lower() in CONNECTORS
