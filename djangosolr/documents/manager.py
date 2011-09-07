import urllib, httplib2, json
from djangosolr.documents.queryset import QuerySet
from django.conf import settings

class ManagerDescriptor(object):
    
    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, type=None):
        if instance != None:
            raise AttributeError("Manager isn't accessible via %s instances" % type.__name__)
        return self.manager

class Manager(object):
    
    def contribute_to_class(self, model, name):
        self._model = model
        setattr(model, name, ManagerDescriptor(self))
        if not getattr(model, '_default_manager', None):
            model._default_manager = self
            
    def _request(self, method, path, query=None, body=None):
        try:
            uri = '%s%s?wt=json' % (settings.DJANGOSOLR_URL, path,)
            if query:
                uri += '&' + urllib.urlencode(query)
            if body:
                body = json.dumps(body)
            headers, body = httplib2.Http().request(uri=uri, method=method, body=body, headers={'Content-type': 'application/json'})
            if headers['status'] == '200':
                return json.loads(body)
            raise Exception(body)
        except:
            raise
    
    def _get_query_set(self):
        return QuerySet(self._model)
    
    def all(self):
        return self._get_query_set().set('fq', settings.DJANGOSOLR_TYPE_FIELD + ':' + self._model._meta.type)
    
    def get(self, id):
        return self._get_query_set().set('q', settings.DJANGOSOLR_ID_FIELD + ':' + str(id))
    
    def clear(self):
        return self._request('POST', settings.DJANGOSOLR_DELETE_PATH, None, {'delete': { 'query': settings.DJANGOSOLR_TYPE_FIELD + ':' + self._model._meta.type}})

def ensure_default_manager(cls):
    if not getattr(cls, '_default_manager', None):
        cls.add_to_class('documents', Manager())
        cls._base_manager = cls.documents
    elif not getattr(cls, '_base_manager', None):
        default_mgr = cls._default_manager.__class__
        if (default_mgr is Manager):
            cls._base_manager = cls._default_manager
        else:
            for base_class in default_mgr.mro()[1:]:
                if (base_class is Manager):
                    cls.add_to_class('_base_manager', base_class())
                    return
            raise AssertionError("Should never get here. Please report a bug, including your model and model manager setup.")