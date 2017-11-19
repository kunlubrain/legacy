import re

#
# DATA holder
#

class Name2Id:
    def __init__(self):
        self._map = {}

    def add(self, name):
        if not name in self._map:
            self._map[name]={}
            self._map[name]['ID'] = len(self._map)+1
            #print "--- add ", name, " id=",self._map[name][0]
        return self._map[name]['ID']
    def len(self): return len(self._map)

    def nextRecText(self):
        for _name, _map in self._map.items():
            yield '!I$%s!X$%s'%(_map['ID'], _name)

    def get(self):
        return self._map

class AuthorRec(Name2Id):
    def __init__(self):
        Name2Id.__init__(self)

    def addRec(self, nm, rec, data):
        if(not rec in self._map[nm]):
            self._map[nm][rec] = []
        if not data: return
        self._map[nm][rec].append(data)

    def addDepart(self, nm, departIDs):
        self.addRec(nm, 'DEPART', departIDs)

    def addPaper(self, nm, paperID):
        self.addRec(nm, 'PAPER', paperID)

    def nextRecText(self):
        for nm, rec in self._map.items():
            departs = ','.join(rec['DEPART'])
            papers  = ','.join(rec['PAPER'])
            text = '!I$%s!X$%s!P$%s!P$%s'%(rec['ID'], nm, departs, papers)
            yield text

class PublisherRec(Name2Id):
    def __init__(self):
        Name2Id.__init__(self)

class DepartRec():
    def __init__(self):
        self._map = {'THIS_ID':0} # company -> department -> [id, geo]

    def get(self):
        self._map.pop('THIS_ID')
        return self._map

    def nextRecText(self):
        for comp, map2 in self._map.items():
            if type(map2)==type(1): continue
            for depart, rec in map2.items():
                text = ''
                _id = rec[0]
                geo = rec[1]
                text += '%s#%s#%s#%s'%(_id, depart, comp, geo)
                yield text

    def add(self, deptText):

        fields = deptText.split(',')
        if not len(fields) > 2: return 0

        # department, [institute], unitversity, city, [state] [country]

        def _normalize(fields):
          fields = [f.strip() for f in fields]
          fields = [re.sub('([A-Z]+)\..*', r'\g<1>', f) for f in fields]
          #print "raw:", fields
          fields = [f for f in fields if re.match('^(\w\w+[\w\s]*|U)', f, re.UNICODE)]
          fields = [f for f in fields if not re.search('^\d+', f)]
          fields = [f for f in fields if not re.search('[:@\+]', f)]
          #print "new:", fields
          fields = [f for f in fields if(re.match('[A-Za-z]', f[0])) ]
          newfields=''
          for i, f in enumerate(fields):
              if not ' ' in f:
                  newfields = fields[:min(i+3, len(fields))]
                  break
          if newfields: fields = newfields
          #print "end:", fields
          return [re.sub('.*:', ' ', f) for f in fields]

        try:
          fields = _normalize(fields)
        except:
          print "\n!!! Problem parsing the department text"
          print "TEXT:", deptText
          print "FIELDS", fields
          fields = _normalize(fields)

        def _findGeo(fields, debug=0):
            if debug: print "find geo for fields", fields
            if debug: print "raw text: ", deptText

            numFields = len(fields)
            depart  = fields[0]
            for i, field in enumerate(fields):
                if (i>=numFields-3) and len(field.split())<=2:
                    geo = ','.join(fields[i:])
                    company = fields[i-1]
                    return depart, company, geo
            company = fields[-1]
            return depart, company, ""

        try:
          depart, company, geo = _findGeo(fields)
        except:
          depart, company, geo = _findGeo(fields, debug=1)

        if not company in self._map: self._map[company]={}
        if not depart in self._map[company]:
            self._map['THIS_ID']+=1
            self._map[company][depart] = [self._map['THIS_ID'], geo]

        return self._map[company][depart][0]
