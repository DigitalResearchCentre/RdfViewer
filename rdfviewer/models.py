from rdfviewer import db
from rdflib.term import URIRef
from rdflib.namespace import Namespace
import urllib2

ns_dict = {
    'xml': Namespace('http://www.w3.org/XML/1998/namespace'),
    'rdf': Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
    'rdfs': Namespace('http://www.w3.org/2000/01/rdf-schema#'),
    'purl': Namespace('http://purl.org/dc/terms/'),
    'owl': Namespace('http://www.w3.org/2002/07/owl#'),
    'drc': Namespace('http://textualcommunities.usask.ca/'),
}
class Model(object):
    owlclass = ns_dict['owl']['Thing']

    @classmethod
    def sparql(cls, query):
        return db.sparql(query)

    @classmethod
    def all(cls):
        query = 'SELECT ?object WHERE {?object a %s}' % cls.owlclass.n3()
        return [cls(r['object']) for r in cls.sparql(query)]

    @classmethod
    def get(cls, uri):
        if not isinstance(uri, URIRef):
            uri = URIRef(uri)
        return cls(uri)

    @property
    def label(self):
        if not hasattr(self, '_label'):
            query = '''
            SELECT ?label WHERE {
                %s %s ?label
            }
            ''' % (self.n3(), ns_dict['rdfs']['label'].n3())
            self._label = self.sparql(query)[0]['label']
        return self._label

    def __init__(self, uri):
        self.uri = uri

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uri == other.uri

    def __ne__(self, other):
        return not self.__eq__(other)

    def json(self):
        return {'label': self.label, 'uri': self.uri.decode()}

    def n3(self):
        a = self.uri
        return self.uri.n3()

    def get_children_uri(self):
        parts = []
        query = '''
        SELECT ?part WHERE {
            %s %s ?part
        }
        ''' % (self.n3(), ns_dict['purl']['hasPart'].n3())
        results = self.sparql(query)
        while results:
            current = URIRef(results[0]['part'])
            parts.append(current)
            query = '''
            SELECT ?part WHERE{
                %s %s ?part
            }
            ''' % (current.n3(), ns_dict['drc']['next'].n3())
            results = self.sparql(query)
        return parts[:-1] # last one will be null, so delete it

    def move(self, num):
        if num == 0: return self
        itor1 = ns_dict['drc']['previous'].n3()
        itor2 = ns_dict['drc']['next'].n3()
        if num > 0:
            itor1, itor2 = itor2, itor1
        query = '''
        SELECT ?r WHERE {
            %s  %s  ?r.
        }
        ''' % (self.n3(), itor1)
        print query
        result = self.sparql(query)[0]
        if result['r'] == ns_dict['rdf']['nil']:
            query = '''
            SELECT ?r WHERE {
                %s  purl:isPartOf   ?parent.
                ?parent %s  ?prev_parent.
                ?r  purl:isPartOf    ?prev_parent.
                ?r  %s   rdf:null.
            }
            ''' % (self.n3(), itor1, itor2)
            result = self.sparql(query)
        num = num + 1 if num < 0 else num - 1
        return self.__class__(result['r']).move(num) if result else None

    def prev(self):
        return self.move(-1)

    def next(self):
        return self.move(1)

class Work(Model):
    owlclass = ns_dict['drc']['Work']

    def hasTextOf(self):
        query = '''
        SELECT ?text WHERE{
            %s %s ?text
        }
        ''' % (self.n3(), ns_dict['drc']['hasTextOf'].n3())
        return [Text(r['text']) for r in self.sparql(query)]

    def hasPart(self):
        return [WorkPart(uri) for uri in self.get_children_uri()]

class WorkPart(Work):
    owlclass = ns_dict['drc']['WorkPart']

    def hasTextOf(self):
        return [TextPart(work.uri) for work in Work.hasTextOf(self)]

class Document(Model):
    owlclass = ns_dict['drc']['Document']

    def hasTextIn(self):
        query = '''
        SELECT ?text WHERE{
            %s %s ?text
        }
        ''' % (self.n3(), ns_dict['drc']['hasTextIn'].n3())
        return [Text(r['text']) for r in self.sparql(query)]

    def hasPart(self):
        return [DocumentPart(uri) for uri in self.get_children_uri()]

class DocumentPart(Document):
    owlclass = ns_dict['drc']['DocumentPart']

    def hasTextIn(self):
        return [TextPart(text.uri) for text in Document.hasTextIn(self)]

class Text(Model):
    owlclass = ns_dict['drc']['Text']

    def isTextOf(self):
        query = '''
        SELECT ?work WHERE{
            %s %s ?work
        }
        ''' % (self.n3(), ns_dict['drc']['isTextOf'].n3())
        return [Work(r['work']) for r in self.sparql(query)]

    def isTextIn(self):
        query = '''
        SELECT ?doc WHERE{
            %s %s ?doc
        }
        ''' % (self.n3(), ns_dict['drc']['isTextIn'].n3())
        return [Document(r['doc']) for r in self.sparql(query)]

    def hasPart(self):
        return [TextPart(uri) for uri in self.get_children_uri()]

class TextPart(Text):
    owlclass = ns_dict['drc']['TextPart']

    def isTextOf(self):
        return [WorkPart(text.uri) for text in Text.isTextOf(self)]

    def isTextIn(self):
        return [DocumentPart(text.uri) for text in Text.isTextIn(self)]

    def hasTranscript(self):
        query = '''
        SELECT ?webAddress WHERE {
            %s %s ?transcript.
            ?transcript %s ?webAddress
        }
        ''' % (self.n3(), ns_dict['drc']['hasTranscript'].n3(),
               ns_dict['drc']['webAddress'].n3())
        result = self.sparql(query)[0]
        print result['webAddress']
        response = urllib2.urlopen(result['webAddress'])
        xml = response.read()
        return xml

    def hasImage(self):
        query = '''
        SELECT ?webAddress WHERE {
            %s %s ?image.
            ?image %s ?webAddress
        }
        ''' % (self.n3(), ns_dict['drc']['hasImage'].n3(),
               ns_dict['drc']['webAddress'].n3())
        return [r['webAddress'] for r in self.sparql(query)]

class Page(TextPart):
    @classmethod
    def get(cls, uri=None, line=None, doc=None):
        if uri:
            return super(Page, cls).get(uri)
        elif not line or not doc:
            raise Exception('both line and doc parameter is needed')
        query = '''
        SELECT ?page_text WHERE {
            ?line_text %s %s.
            ?line_text %s ?doc.
            ?doc %s %s.
            ?doc %s ?page_text 
        }
        ''' % (ns_dict['drc']['isTextOf'].n3(), line.n3(), 
               ns_dict['drc']['isTextIn'].n3(),
               ns_dict['purl']['isPartOf'].n3(), doc.n3(),
               ns_dict['drc']['hasTextIn'].n3())
        print query
        result = cls.sparql(query)
        if len(result) > 1:
            raise Exception('multiple result returned')
        return cls(result[0]['page_text'])

    def next(self):
        doc = self.isTextIn()[0]
        return doc.next().hasTextIn()[0]

    def prev(self):
        doc = self.isTextIn()[0]
        return doc.prev().hasTextIn()[0]

