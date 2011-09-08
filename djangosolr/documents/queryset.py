from django.conf import settings
from django.utils import tree
import re

FILTER_CONTAINS = u'%s:%s'
FILTER_EXACT = u'%s:"%s"'
FILTER_COMPARE = {
    'gt': u'%s:{%s TO *}',
    'gte': u'%s:[%s TO *]',
    'lt': u'%s:{* TO %s}',
    'lte': u'%s:[* TO %s]',
}

FILTER_RANGE = {
    'range': u'%s:[%s TO %s]',
    'rangecc': u'%s:[%s TO %s]',
    'rangeoc': u'%s:{%s TO %s]',
    'rangeco': u'%s:[%s TO %s}',
    'rangeoo': u'%s:{%s TO %s}'
}
WHITESPACE_RE = re.compile(r'\s+')

class Q(tree.Node):
    
    AND = 'AND'
    OR = 'OR'
    default = AND

    def __init__(self, *args, **kwargs):
        super(Q, self).__init__(children=list(args) + kwargs.items())

    def _combine(self, other, conn):
        if not isinstance(other, Q):
            raise TypeError(other)
        obj = Q()
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = Q()
        obj.add(self, self.AND)
        obj.negate()
        
    def get_query_string(self, meta):
        query = []
        for child in self.children:
            if isinstance(child, basestring):
                query.append(child)
            elif hasattr(child, 'get_query_string'):
                query.append(child.get_query_string(meta))
            else:                
                filter, value = child
                fn, _, ft = filter.partition('__')
                f = meta.get_field(fn)
                fn = meta.get_solr_field_name(fn)
                if not ft or ft == 'contains':
                    if isinstance(value, basestring):
                        queryt = []
                        for value in WHITESPACE_RE.split(value):
                            queryt.append(FILTER_CONTAINS % (fn, f.prepare(value),))
                        s = u' AND '.join(queryt)
                        if len(queryt) > 1:
                            s = u'(%s)' (s,)
                        query.append(s)
                    else:
                        query.append(FILTER_CONTAINS % (fn, f.prepare(value),))
                elif ft == 'exact':
                    query.append(FILTER_EXACT % (fn, f.prepare(value),))
                elif ft in FILTER_COMPARE:
                    value = u'"%s"' % (f.prepare(value),) if isinstance(value, basestring) else f.prepare(value)  
                    query.append(FILTER_COMPARE[ft] % (ft, value,))
                elif ft in FILTER_RANGE:
                    value1, value2 = value
                    value1 = u'"%s"' % (f.prepare(value1),) if isinstance(value1, basestring) else f.prepare(value1)
                    value2 = u'"%s"' % (f.prepare(value2),) if isinstance(value2, basestring) else f.prepare(value2)
                    query.append(FILTER_RANGE[ft] % (fn, value1, value2,))
                elif ft == 'in':
                    query.append(u'(%s)' % (' OR '.join([u'%s:%s' % (fn, f.prepare(v),) for v in value]),))                
                else:
                    raise NotImplementedError
        s = (u' %s ' % (self.connector,)).join(query)
        if self.negated:
            s = u'NOT (%s)' % (s,)
        elif len(self.children) > 1:
            s = u'(%s)' % (s,)
        return s
    
class Query(object):
    
    def __init__(self):
        self._q = Q()
        self._fq = Q()
        self._sort = []
        self._params = {}
        
    def clone(self):
        clone = Query()
        clone._q = self._q
        clone._fq = self._fq
        clone._sort.extend(self._sort) 
        clone._params.update(self._params)
        return clone
    
    def q(self, *qs, **filters):
        for q in qs:
            self._q &= q
        if filters:
            self._q &= Q(**filters)
               
    def fq(self, *qs, **filters):
        for q in qs:
            self._fq &= q
        if filters:
            self._fq &= Q(**filters) 
    
    def sort(self, *fields):
        self._sort.extend(fields)
    
    def raw(self, **kwargs):
        self._params.update(kwargs)
        
    def set_limits(self, start, stop):
        if start is not None:
            self._params['start'] = start
        elif 'start' in self._params:
            del self._params['start']
        if stop is not None:
            self._params['rows'] = stop - (start or 0)
        elif 'rows' in self._params:
            del self._params['rows']
            
    def get_query_string(self, meta):
        query = []
        #raw params
        for k, v in self._params.items():
            query.append((k, v,))

        #q
        if not self._q:
            self._q = Q('*:*')
        query.append(('q', self._q.get_query_string(meta),))
        
        #fq        
        self._fq &= Q('%s:%s' % (meta.get_solr_type_field(), meta.get_solr_type_value(),))
        query.append(('fq', self._fq.get_query_string(meta),))

        #sort
        if self._sort:
            sort = ','.join(['%s desc' % (meta.get_solr_field_name(field[1:]),) if field.startswith('-')
                             else '%s asc' % (meta.get_solr_field_name(field),)
                             for field in self._sort])
            query.append(('sort', sort,))
        
        return query

class QuerySet(object):
    
    def __init__(self, model, query=None):
        self._model = model
        self._query = query or Query()
        self._response = None
        
        self._result_cache = None
        self._iter = None
        
    def _get_response(self):
        if self._response is None:
            self._response = self._model._default_manager.request('GET', settings.DJANGOSOLR_SELECT_PATH, self._query.get_query_string(self._model._meta))
        return self._response
    response = property(_get_response) 
    
    def _clone(self):
        return QuerySet(self._model, self._query.clone())
    
    def __len__(self):
        if self._result_cache is None:
            if self._iter:
                self._result_cache = list(self._iter)
            else:
                self._result_cache = list(self.iterator())
        elif self._iter:
            self._result_cache.extend(self._iter)
        return len(self._result_cache)

    def __iter__(self):
        if self._result_cache is None:
            self._iter = self.iterator()
            self._result_cache = []
        if self._iter:
            return self._result_iter()
        return iter(self._result_cache)
    
    def _result_iter(self):
        pos = 0
        while 1:
            upper = len(self._result_cache)
            while pos < upper:
                yield self._result_cache[pos]
                pos = pos + 1
            if not self._iter:
                raise StopIteration
            if len(self._result_cache) <= pos:
                self._fill_cache()
                
    def _fill_cache(self, num=None):
        if self._iter:
            try:
                for _ in range(num or 100):
                    self._result_cache.append(self._iter.next())
            except StopIteration:
                self._iter = None

    def __nonzero__(self):
        if self._result_cache is not None:
            return bool(self._result_cache)
        try:
            iter(self).next()
        except StopIteration:
            return False
        return True

    def __getitem__(self, k):
        if not isinstance(k, (slice, int, long)):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0))
                or (isinstance(k, slice) and (k.start is None or k.start >= 0)
                    and (k.stop is None or k.stop >= 0))), \
                "Negative indexing is not supported."

        if self._result_cache is not None:
            if self._iter is not None:
                if isinstance(k, slice):
                    if k.stop is not None:
                        bound = int(k.stop)
                    else:
                        bound = None
                else:
                    bound = k + 1
                if len(self._result_cache) < bound:
                    self._fill_cache(bound - len(self._result_cache))
            return self._result_cache[k]

        if isinstance(k, slice):
            qs = self._clone()
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None
            qs._query.set_limits(start, stop)
            return k.step and list(qs)[::k.step] or qs
        try:
            qs = self._clone()
            qs._query.set_limits(k, k + 1)
            return list(qs)[0]
        except:
            raise IndexError(0)
                
    def iterator(self): 
        for doc in self.response['response']['docs']:
            yield self._model.create(doc)
    
    def sort(self, *fields):
        clone =  self._clone()
        clone._query.sort(*fields)
        return clone
    
    def count(self):
        response = self._get_response()
        return response['response']['numFound']
    
    def raw(self, **kwargs):
        clone =  self._clone()
        clone._query.raw(**kwargs)
        return clone
    
    def q(self, *qs, **filters):
        clone =  self._clone()
        clone._query.q(*qs, **filters)
        return clone
    
    def fq(self, *qs, **filters):
        clone =  self._clone()
        clone._query.fq(*qs, **filters)
        return clone
