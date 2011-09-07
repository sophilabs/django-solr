import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'
from example.movies.documents import MovieDocument

MovieDocument.documents.clear()

MovieDocument(title='Jurassic Park I', director='Steven Spielberg').save()

print list(MovieDocument.documents.all())