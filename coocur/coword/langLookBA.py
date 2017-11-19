import langHardStop as ss

# CONDITIONED NOISE -- look behind noise

# ---------------------------
# LB-NOISE-SIGNAL-LIST + WORD
# ---------------------------

LB_STOP = {
  "mechanism" : ["possible "],
  "presents" : ["article", "paper", "letter", "work", "brief", "study"],
  "shows" : ["article", "paper", "letter", "work", "brief", "study", "experiment"],
  "show" : ["results", "result", "article", "paper", "letter", "work", "brief", "study",
            "experiment"],
  "showed" : ["results", "result", "article", "paper", "letter", "work", "brief", "study",
              "experiment"],
  "results" : ["experimental", "simulation", "measurement", "measured", "calculated",
               "numerical", "theoretical", "simulated", "analytical", "test", "computed",
               "preliminary", "reported", "previous", "modeling", "accurate"],
  "reports" : ["article", "paper", "letter", "work", "brief", "study", "experiment"],
  "values" : ["measured", "calculated", ],
  "analysis" : ["statistical", "quantitative", "simple", "theoretical", "detailed",
                "numerical"],
  "rise" : ["give", "gives", "giving", ],
  "model" : ["accurate", "simple", "developed", "developped", "previous", "proposed",  ],
  "models" : ["accurate", "simple", "developed", "developped", "previous", "proposed", ],
  "account" : ["into", "takes" ],
  "accounts" : ["into", "takes" ],
  "method" : ["proposed", "simple", "efficient", "effective", "accurate", "novel",
              "conventional"],
  "measurement" : ["proposed", "simple", "efficient", "effective", "accurate", "conventional"],
  "papers" : ["aforementioned", "authors", "classic", "comments", "companion", "covered",
              "current", "discussed", "downloaded", "earlier", "following", "full",
              "individual", "initial", "introductory", "involving", "known", "mentioned",
              "named", "original", "overall", "preceding", "preselected", "present",
              "previous", "published", "recent", "referenced", "review", "second", "seminal",
              "separate", "short", "technical", "theoretical", "third", "tutorial", "sister",
              "titled",] + ss.DeterminerGeneral,
  "work" : ["additional", "basic", "considerable", "current", "earlier", "early",
            "experimental", "further", "later", "most", "much", "preliminary", "previous",
            "prior", "recent", "research", "some", "theoretical", "accurate", "apparent",
            "appropriate", "assumed", "authors", "breaking", "can", "compatible",
            "comprehensive", "considerable", "could", "current", "definitive", "development",
            "different", "effective", "effectively", "elaborations", "experimental",
            "exploratory", "external", "first", "following", "foregoing", "future", "given",
            "high", "higher", "induced", "initial", "laboratory", "laborious", "little",
            "mathematical", "mentioned", "monitoring", "more", "much", "must", "named",
            "novel", "numerical", "ongoing", "original", "pioneering", "possible", "practical",
            "preliminary", "present", "previous", "prior", "proper", "proposed", "prospective",
            "provide", "published", "recent", "related", "reported", "reports", "research",
            "right", "same", "similar", "single", "technique", "theoretical", "titled",
            "useful", ] + ss.DeterminerGeneral,
  "article" : [] + ss.DeterminerGeneral,
}

# ---------------------------
# LOOK-AHEAD stops
# ---------------------------

LA_STOP = {
  "experimental" : ["data", "measurement", "evidence", "observations", "study",
                    "studies", "demonstration", "technique", "techniques", "method",
                    "result", "conditions", "work", "verification", "values", "devices"],

  "different" : ["value", "methods", "kinds", "approach", "approches", "levels",],
  "account" : ["for"],
  "accounts" : ["for"],
  "accounting" : ["for"],
}

# ---------------------------
# look-in-Sentence stops
# ---------------------------
LS_STOP = {
    "overview" : ['article', 'paper', 'work', 'letter', 'brief', 'study']
}

# all "neutral" verbs should be checked using LOOK-BEHIND
# took
# task
# activity/activities

# improved reliability::20::30098::0.000664495979799
# excellent characteristics::20::30098::0.000664495979799

#  --- handling of "account"
#  check its leading and trailing words (take into account, account for, ...)
#  in the case "personal account", keep it as a noun

# highest reported::21::30098::0.000697720778789

# outlines work ...
# <-- noun-verb is a verb if appearing at first and in plural form
# exception: standards activities 
# little work is : perhaps both look behind and ahead?,
