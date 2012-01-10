from djangosolr.documents.queryset import QuerySet
from djangosolr.documents.query import Q
from django.conf import settings
from djangosolr import solr

class ManagerDescriptor(object):
    
    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, type=None):
        if instance != None:
            raise AttributeError("Manager isn't accessible via %s instances" % type.__name__)
        return self.manager

class Manager(object):
    
    def _contribute_to_class(self, model, name):
        self._model = model
        setattr(model, name, ManagerDescriptor(self))
        if not getattr(model, '_default_manager', None):
            model._default_manager = self
    
    def _get_query_set(self):
        return QuerySet(self._model)
    
    def all(self):
        return self._get_query_set()
    
    def raw(self, **kwargs):
        return self._get_query_set().raw(**kwargs)
    
    def q(self, *qs, **filters):
        return self._get_query_set().q(*qs, **filters)
    
    def fq(self, *qs, **filters):
        return self._get_query_set().fq(*qs, **filters)
    
    def fl(self, *fields):
        return self._get_query_set().fl(*fields)
    
    def sort(self, *fields):
        return self._get_query_set().sort(*fields)
    
    def get(self, id):
        pk = self._model._meta.pk
        return self._get_query_set().q(Q('%s:%s-%s' % (settings.DJANGOSOLR_ID_FIELD, self._model._meta.type, pk.prepare(id),)))[0]

    def delete(self, *qs, **filters):
        return self._get_query_set().delete(*qs, **filters)
    
    def clear(self):
        return solr.clear(self._model)

def ensure_default_manager(cls):
    if not getattr(cls, '_default_manager', None):
        cls._add_to_class('documents', Manager())
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