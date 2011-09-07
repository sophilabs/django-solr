from djangosolr.documents.options import Options
from djangosolr.documents.manager import ensure_default_manager
from django.conf import settings

class DocumentBase(type):
    
    def __new__(cls, name, bases, attrs):
        super_new = super(DocumentBase, cls).__new__
        new_class = super_new(cls, name, bases, {'__module__': attrs.pop('__module__')})
        
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        new_class.add_to_class('_meta', Options(meta))

        if getattr(new_class, '_default_manager', None):
            new_class._default_manager = None
            new_class._base_manager = None

        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        new_class._prepare()
        
        return new_class
    
    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)
    
    def _prepare(cls):
        opts = cls._meta
        opts._prepare(cls)
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
                name = cls._meta.type + '-' + field.name
                if om.has_key(name):
                    setattr(document, field.name, field.convert(om[name]))
        else:
            for field in cls._meta.fields:
                setattr(document, field.name, getattr(om, field.name))
        return document
    
    def save(self):
        id = getattr(self, self._meta.pk.name)
        type = self._meta.type
        doc = {settings.DJANGOSOLR_ID_FIELD: type + '-' + str(id), settings.DJANGOSOLR_TYPE_FIELD: type}
        for field in self._meta.fields:
            value = field.prepare(getattr(self, field.name))
            if value is None:
                doc[type + '-' + field.name] = [] #BUG: https://issues.apache.org/jira/browse/SOLR-2714
            else:    
                doc[type + '-' + field.name] = value 
        return self._default_manager._request('POST', settings.DJANGOSOLR_UPDATE_PATH, [('commit', 'true',)], { 'add': { 'overwrite': True, 'doc': doc}, 'commit': {} })
    
    def delete(self):
        id = getattr(self, self._meta.pk.name)
        type = self._meta.type
        return self._default_manager._request('POST', settings.DJANGOSOLR_DELETE_PATH, None, {'delete': { 'query': settings.DJANGOSOLR_ID_FIELD + ':' + type + '-' + str(id)}, 'commit': {} })
