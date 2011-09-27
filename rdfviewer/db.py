import urllib, urllib2, settings
from lxml import etree
from rdflib.term import URIRef, BNode, Literal

class SPARQLResultParseError(Exception):
    pass

class SPARQLResult(dict):
    namespaces = {'ns':'http://www.w3.org/2005/sparql-results#'}

    def __init__(self, element):
        binding_type = {
            'uri': '{%s}uri' % self.namespaces['ns'],
            'literal': '{%s}literal' % self.namespaces['ns'],
            'bnode': '{%s}bnode' % self.namespaces['ns'],
        }
        for binding in element.xpath('ns:binding', namespaces=self.namespaces):
            node = binding.getchildren()[0]
            value = node.text.strip()
            if node.tag == binding_type['uri']:
                self[binding.attrib['name']] = URIRef(value)
            elif node.tag == binding_type['literal']:
                ns = 'http://www.w3.org/XML/1998/namespace'
                lang = node.get('{%s}lang' % ns, default=None)
                datatype = node.get('datatype', default=None)
                self[binding.attrib['name']] = Literal(value, lang=lang, 
                                                       datatype=datatype)
            elif node.tag == binding_type['bnode']:
                self[binding.attrib['name']] = BNode(value)
            else:
                raise SPARQLResultParseError('Can not parse: %s' %
                                             etree.tostring(node));

    @classmethod
    def parseXML(cls, xml):
        root = etree.XML(xml)
        elements = root.xpath('//ns:result', namespaces=cls.namespaces)
        results = []
        for element in elements:
            results.append(cls(element))
        return results

class DBConnectionError(Exception):
    pass

def sparql(query):
    sparql_endpoint = getattr(settings, 'sparql_endpoint', None) or \
            'http://localhost:8000/sparql/'
    data = urllib.urlencode({'query': query})
    try:
        response = urllib2.urlopen(sparql_endpoint, data)
    except urllib2.URLError, e:
        raise DBConnectionError('%s:%s query: %s' % 
                                (str(e), sparql_endpoint, query))
    results = SPARQLResult.parseXML(response.read())
    response.close()
    return results

def append_graph(graph_uri, triples):
    raise Exception('testing method, not implement right')
    sparql_endpoint = 'http://localhost:8000/data/'
    data = urllib.urlencode({
        'graph': graph_uri,
        'data': triples,
        'mime-type': 'application/x-turtle',
    })
    try:
        response = urllib2.urlopen(sparql_endpoint, data)
    except urllib2.URLError, e:
        raise DBConnectionError('%s:%s graph: %s, data: %s' % 
                                (str(e), sparql_endpoint, graph_uri, triples))


