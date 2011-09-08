from djangosolr.documents.options import Options
from djangosolr.documents.manager import ensure_default_manager
from django.conf import settings
from djangosolr.documents.util import escape

class DocumentBase(type):
    
    def __new__(cls, name, bases, attrs):
        super_new = super(DocumentBase, cls).__new__
        new_class = super_new(cls, name, bases, {'__module__': attrs.pop('__module__')})
        
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        new_class._add_to_class('_meta', Options(meta))

        if getattr(new_class, '_default_manager', None):
            new_class._default_manager = None
            new_class._base_manager = None

        for obj_name, obj in attrs.items():
            new_class._add_to_class(obj_name, obj)

        new_class._prepare_class()
        
        return new_class
    
    def _add_to_class(cls, name, value):
        if hasattr(value, '_contribute_to_class'):
            value._contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)
    
    def _prepare_class(cls):
        opts = cls._meta
        opts._prepare_class(cls)
        ensure_default_manager(cls)

class Document(object):
    
    __metaclass__ = DocumentBase
    
    def __init__(self, **kwargs):
        for field in self._meta.fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs.pop(field.name))
            else:
                setattr(self, field.name, field.get_default())
        if kwargs:
            raise KeyError(kwargs.keys()[0])
    
    @classmethod
    def create(cls, om):
        document = cls()
        if isinstance(om, dict):
            for field in cls._meta.fields:
                name = cls._meta.get_solr_field_name(field)
                if om.has_key(name):
                    setattr(document, field.name, field.convert(om[name]))
        else:
            for field in cls._meta.fields:
                setattr(document, field.name, getattr(om, field.name))
        return document
    
    def save(self):
        m = self._meta
        doc = { m.get_solr_id_field(): m.get_solr_id_value(self),
                m.get_solr_type_field(): m.get_solr_type_value()}
        for field in self._meta.fields:
            value = field.prepare(getattr(self, field.name))
            if value is None:
                doc[m.get_solr_field_name(field)] = [] #BUG: https://issues.apache.org/jira/browse/SOLR-2714
            else:    
                doc[m.get_solr_field_name(field)] = value 
        return self._default_manager.request('POST', settings.DJANGOSOLR_UPDATE_PATH, [('commit', 'true',)], { 'add': { 'overwrite': True, 'doc': doc}, 'commit': {} })
    
    def delete(self):
        m = self._meta
        return self._default_manager.request('POST', settings.DJANGOSOLR_DELETE_PATH, None, {'delete': { 'query': u'%s:%s' % (m.get_solr_id_field(), escape(m.get_solr_id_value(self)),)}, 'commit': {} })
