import datetime, decimal

class Field():
    
    def __init__(self, type='string', name=None, stored=True, indexed=True, multivalued=False, primary_key=False):
        self.type = type
        self.name = name
        self.stored = stored
        self.indexed = indexed
        self.multivalued = multivalued
        self.primary_key = primary_key
        
    def _contribute_to_class(self, cls, name):
        self.name = name
        self._model = cls
        cls._meta.add_field(self)
        
    def get_default(self):
        return None
        
    def prepare(self, value):
        return value
    
    def convert(self, value):
        return value
    
class IntegerField(Field):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('type', 'int')
        Field.__init__(self, **kwargs)

class CharField(Field):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('type', 'string')
        Field.__init__(self, **kwargs)

class DateTimeField(Field):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('type', 'date')
        Field.__init__(self, **kwargs)
    
    def prepare(self, value):
        return value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    def convert(self, value):
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            return datetime.datetime.strptime(value, '%Y-%m-%d').date()
    
class FloatField(Field):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('type', 'float')
        Field.__init__(self, **kwargs)
        
class TextField(Field):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('type', 'text')
        Field.__init__(self, **kwargs)

class DecimalField(Field):
    
    def __init__(self, **kwargs):
        kwargs.setdefault('type', 'float')
        Field.__init__(self, **kwargs)

    def prepare(self, value):
        return float(value)
    
    def convert(self, value):
        return decimal.Decimal(value)