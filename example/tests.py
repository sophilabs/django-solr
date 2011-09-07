import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'
from example.movies.documents import MovieDocument
from djangosolr.documents import Q


#Delete all movies
MovieDocument.documents.clear()

#Save movie
MovieDocument(id="1", title='Jurassic Park I', director='Steven Spielberg').save()
MovieDocument(id="2", title='Jurassic Park III', director='Joe Johnston').save()

#Get by id
m = MovieDocument.documents.get(1)

#Get all movies
r = MovieDocument.documents.all().q(Q('text', 'steven') | Q('text', 'joe'))
for m in r:
    print m.id, m.title