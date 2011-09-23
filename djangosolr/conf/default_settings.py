
DJANGOSOLR_ID_FIELD = 'id'
DJANGOSOLR_TYPE_FIELD = 'type'

DJANGOSOLR_FIELD_MAPPING = {
    'django.db.models.fields.AutoField': 'djangosolr.documents.fields.IntegerField',
    'django.db.models.fields.IntegerField': 'djangosolr.documents.fields.IntegerField',
    'django.db.models.fields.BigIntegerField': 'djangosolr.documents.fields.IntegerField',
    'django.db.models.fields.FloatField': 'djangosolr.documents.fields.FloatField',
    'django.db.models.fields.DecimalField': 'djangosolr.documents.fields.DecimalField',
    'django.db.models.fields.TextField': 'djangosolr.documents.fields.CharField',
    'django.db.models.fields.CharField': 'djangosolr.documents.fields.CharField',
    'django.db.models.fields.DateField': 'djangosolr.documents.fields.DateTimeField',
    'django.db.models.fields.DateTimeField': 'djangosolr.documents.fields.DateTimeField',
    'django.db.models.fields.BooleanField': 'djangosolr.documents.fields.BooleanField',
    'django.db.models.fields.NullBooleanField': 'djangosolr.documents.fields.BooleanField',
}

DJANGOSOLR_AUTOCOMMIT = True
DJANGOSOLR_URL = 'http://localhost:8983/solr'
DJANGOSOLR_SELECT_PATH = '/select'
DJANGOSOLR_UPDATE_PATH = '/update/json'
DJANGOSOLR_DELETE_PATH = '/update/json'

DJANGOSOLR_ROWS_PER_QUERY = 2
