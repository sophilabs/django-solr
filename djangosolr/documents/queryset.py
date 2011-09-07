from django.conf import settings
from djangosolr.documents.util import escape

class QBase(object):
    
    def __init__(self):
        pass

    def get_query(self, meta):
        raise NotImplementedError
    
    def __or__(self, other):
        return QOr(self, other)

    def __and__(self, other):
        return QAnd(self, other)

    def __invert__(self):
        return QNot(self)

class Q(QBase):

    def __init__(self, name, value):
        super(Q, self).__init__()
        self.name = name
        self.value = value
    
    def get_query(self, meta):
        field = meta.get_field(self.name)
        return '(%s-%s:%s)' % (meta.type, field.name, escape(unicode(field.prepare(self.value))),)
    
class QRaw(QBase):
    
    def __init__(self, raw):
        self.raw = raw
        
    def get_query(self, meta):
        return self.raw
    
class QRange(QBase):
    
    def __init__(self, name=None, start=None, end=None):
        super(Q, self).__init__()
        self.name = name
        self.start = start
        self.end = end
        
    def get_query(self, meta):
        raise NotImplementedError

class QAnd(object):
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def get_query(self, meta):
        return '(%s AND %s)' % (self.a.get_query(meta), self.b.get_query(meta),)
    
class QOr():
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def get_query(self, meta):
        return '(%s OR %s)' % (self.a.get_query(meta), self.b.get_query(meta),)
    
class QNot(object):
    
    def __init__(self, a):
        self.a = a
        
    def get_query(self, meta):
        return '-(%s)' % (self.a.get_query(meta),)

class Query(object):
    
    def __init__(self):
        self._q = None
        self._fq = None
        self._params = {}
        
    def clone(self):
        clone = Query()
        clone._q = self._q
        clone._fq = self._fq
        clone._params.update(self._params)
        return clone
    
    def q(self, q):
        if self._q:
            self._q = QAnd(self._q, q)
        else:
            self._q = q
            
    def fq(self, fq):
        if self._fq:
            self._fq = QAnd(self._q, fq)
        else:
            self._fq = fq 
    
    def set(self, name, value):
        self._params[name] = value
        
    def set_limits(self, start, stop):
        if start is not None:
            self._params['start'] = start
        elif 'start' in self._params:
            del self._params['start']
        if stop is not None:
            self._params['rows'] = stop - (start or 0)
        elif 'rows' in self._params:
            del self._params['rows']
            
    def get_query(self, meta):
        query = []
        for k, v in self._params.items():
            query.append((k, v,))
        q = QRaw('*:*')
        if self._q:
            q = self._q
        query.append(('q', q.get_query(meta)))        
        fq = QRaw('%s:%s' % (settings.DJANGOSOLR_TYPE_FIELD, meta.type,))
        if self._fq:
            fq = QAnd(self._fq, fq)
        query.append(('fq', fq.get_query(meta)))
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
            self._response = self._model._default_manager.request('GET', settings.DJANGOSOLR_SELECT_PATH, self._query.get_query(self._model._meta))
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
                for i in range(num or 100):
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
    
    def set(self, name, value):
        clone =  self._clone()
        clone._query.set(name, value)
        return clone
    
    def search(self, name, value):
        clone =  self._clone()
        clone._query.q(Q(name, value))
        return clone
    
    def q(self, q):
        clone =  self._clone()
        clone._query.q(q)
        return clone
    
    def fq(self, fq):
        clone =  self._clone()
        clone._query.fq(fq)
        return clone
