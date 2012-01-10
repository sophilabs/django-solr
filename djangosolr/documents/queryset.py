from djangosolr.documents.query import Query, Q
from djangosolr import solr

class QuerySet(object):
    
    def __init__(self, model, query=None):
        self._model = model
        self._query = query or Query()
        self._responses = []
        self._responses_more = True
        self._result_cache = None
        self._iter = None
        
    def _get_responses(self):
        for response in self._responses:
            yield response
        rows = 10 if self._query._rows is None else self._query._rows
        start = len(self._responses) * rows if self._query._start is None else self._query._start
        while self._responses_more:
            query = self._query.clone()
            query.set_limits(start, start + rows)
            response = solr.select(query.get_query_string(self._model._meta))
            start += rows
            self._responses.append(response)
            self._responses_more = self._query._start is None and self._query._rows is None and len(response['response']['docs']) == rows
            yield response
    
    def _get_response(self):
        return self._get_responses().next()
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
                for _ in range(num or 20):
                    self._result_cache.append(self._iter.next())
            except StopIteration:
                self._iter = None
                
    def iterator(self):
        for response in self._get_responses():
            for doc in response['response']['docs']:
                yield self._model.create(doc)       

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
    
    def sort(self, *fields):
        clone =  self._clone()
        clone._query.sort(*fields)
        return clone
    
    def fl(self, *fields):
        clone =  self._clone()
        clone._query.fl(*fields)
        return clone
    
    def count(self):
        return self.response['response']['numFound']
    
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

    def delete(self, *qs, **filters):
        if qs or filters:
            return self.q(*qs, **filters).delete()
        else:
            return solr.delete((self._query._q or Q('*:*')).get_query_string(self._model._meta))