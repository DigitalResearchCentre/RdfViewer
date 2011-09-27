import json, re
from django.http import HttpResponse
from django.shortcuts import render_to_response 
from django.template import RequestContext
from django import forms
from rdfviewer.models import ns_dict, Work, Document, Text
from rdfviewer.models import WorkPart, DocumentPart, TextPart, Page
import urllib2

def index(request):
    works = Work.all()
    return render_to_response(
        'rdfviewer/index.html', {'works': works}, 
        context_instance=RequestContext(request))

def viewer(request):
    work_uri = request.GET.get('work')
    parts = Work.get(work_uri).hasPart()
    part_uri = request.GET.get('part', parts[0].uri)
    cantos = WorkPart.get(part_uri).hasPart()
    canto_uri  = request.GET.get('canto')
    if canto_uri not in [str(c.uri) for c in cantos]:
        canto_uri = cantos[0].uri
    lines = WorkPart.get(canto_uri).hasPart()
    line_uri = request.GET.get('line')
    if line_uri not in [str(l.uri) for l in lines]:
        line_uri = lines[0].uri
    docs = []
    for text in Work.get(work_uri).hasTextOf():
        docs.extend(text.isTextIn())
    doc_uri = request.GET.get('doc', docs[0].uri)
    response_dict = {
        'part': {'selected': part_uri, 'items': [p.json() for p in parts]},
        'canto':{'selected': canto_uri,'items':[c.json() for c in cantos]},
        'line': {'selected': line_uri, 'items': [l.json() for l in lines]},
        'doc': {'selected': doc_uri, 'items': [d.json() for d in docs]}
    }
    if request.GET.get('format') == 'json':
        return HttpResponse(json.dumps(response_dict))
    response_dict['work_uri'] = work_uri
    return render_to_response(
        'rdfviewer/viewer.html', response_dict, 
        context_instance=RequestContext(request))

def page(request):
    page_uri = request.GET.get('page')
    if page_uri:
        page = Page.get(uri=page_uri)
        func = request.GET.get('func')
        if func == 'next':
            page = page.next()
        elif func == 'prev':
            page = page.prev()
    else:
        line = WorkPart.get(request.GET.get('line'))
        doc = Document.get(request.GET.get('doc'))
        page = Page.get(line=line, doc=doc)
    return HttpResponse(json.dumps({
        'page': page.uri,
        'transcript': page.hasTranscript(),
        'image': page.hasImage()
    }))

from xml.dom import minidom
def get_text(dom):
    if dom.nodeType == dom.TEXT_NODE:
        return dom.data
    else:
        return ''.join([get_text(child) for child in dom.childNodes])

def get_tokens(xml):
    dom = minidom.parseString(xml)
    result = []
    xml_doc = dom.childNodes[0]
    l = [child for child in xml_doc.childNodes if child.nodeName == 'l'][0]
    for word in l.childNodes:
        if word.nodeType == dom.TEXT_NODE: continue
        result.append({'t': word.toxml(), 'n': get_text(word)})
    return result

def line(request):
    part = request.GET.get('part', 'Inferno')
    canto = request.GET.get('canto', '1')
    line = request.GET.get('line', '1')
    line_uri = ns_dict['drc']['%s-%s-%s'] % (part, canto, line)
    data = {'witnesses': []}
    for l in WorkPart.get(line_uri).hasTextOf():
        transcript = l.hasTranscript()
        tokens = get_tokens(transcript)
        data['witnesses'].append(
            {'id': str(l.uri).split('-')[-1], 'tokens':tokens})
    request = urllib2.Request(
        'http://gregor.middell.net/collatex/api/collate',
        json.dumps(data),
        {'Content-Type': 'application/json', 'Accept': 'application/json'}
    )
    response = urllib2.urlopen(request)
    return HttpResponse(response.read(), mimetype='application/json')


