from djangosolr.documents.options import Options
from djangosolr.documents.manager import ensure_default_manager
from djangosolr import solr

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
                if hasattr(om, field.name):
                    setattr(document, field.name, getattr(om, field.name))
        return document
    
    def save(self):
        return solr.save([self])

    def pre_save(self):
        pass
    
    def delete(self):
        return solr.delete([self])

    def pre_delete(self):
        pass
