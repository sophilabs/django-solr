from django.conf import settings
import httplib2, json, re, urllib

#http://fragmentsofcode.wordpress.com/2010/03/10/escape-special-characters-for-solrlucene-query/
ESCAPE_CHARS_RE = re.compile(r'(?<!\\)(?P<char>[&|+\-!(){}[\]^"~*?:])')

def escape(value):
    return ESCAPE_CHARS_RE.sub(r'\\\g<char>', value)

def urlencode(query):
    l = []
    for k, v in query:
        k = urllib.quote(unicode(k).encode('utf8'))
        v = urllib.quote(unicode(v).encode('utf8'))
        l.append(k + '=' + v)
    return '&'.join(l)

def request(method, path, query=None, body=None):
    try:
        uri = '%s%s?wt=json' % (settings.DJANGOSOLR_URL, path,)
        if query:
            uri += '&' + urlencode(query)
        if body:
            body = json.dumps(body)
        headers, body = httplib2.Http().request(uri=uri, method=method, body=body, headers={'Content-type': 'application/json'})
        if headers['status'] == '200':
            return json.loads(body)
        raise Exception(body)
    except:
        raise
    
def select(query):
    return request('GET', settings.DJANGOSOLR_SELECT_PATH, query)
    
def save(docs, commit=True, overwrite=True):
    ddocs = []
    for doc in docs:
        m = doc._meta
        doc.pre_save()
        ddoc = { m.get_solr_id_field(): m.get_solr_id_value(doc),
                 m.get_solr_type_field(): m.get_solr_type_value()}
        for field in doc._meta.fields:
            value = field.prepare(getattr(doc, field.name))
            if value is None:
                ddoc[m.get_solr_field_name(field)] = [] #BUG: https://issues.apache.org/jira/browse/SOLR-2714
            else:    
                ddoc[m.get_solr_field_name(field)] = value
        ddocs.append(ddoc)
    return request('POST', settings.DJANGOSOLR_UPDATE_PATH, [('commit', str(commit).lower(),), ('overwrite', str(overwrite).lower())], { 'add': ddocs })

def delete(query, commit=True):
    if not isinstance(query, basestring):
        queries = []
        for doc in query:
            m = doc._meta
            doc.pre_delete()
            queries.append(u'%s:%s' % (m.get_solr_id_field(), escape(m.get_solr_id_value(doc))))
        query = ' OR '.join(queries)
    return request('POST', settings.DJANGOSOLR_DELETE_PATH, [('commit', str(commit).lower(),)], {'delete': { 'query': query }})

def clear(model, commit=True):
    return request('POST', settings.DJANGOSOLR_DELETE_PATH, [('commit', str(commit).lower(),)], {'delete': { 'query': settings.DJANGOSOLR_TYPE_FIELD + ':' + model._meta.type}})
