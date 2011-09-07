import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'
from example.movies.documents import MovieDocument
from djangosolr.documents import Q


#Delete all movies
#MovieDocument.documents.clear()

x = MovieDocument.documents.all()[:1]
print len(x)
print x.count()

#Save some movies
#MovieDocument(id="1", title='Jurassic Park I', director='Steven Spielberg').save()
#MovieDocument(id="2", title='Jurassic Park III', director='Steven Spielberg').save()

#Get and update a movie by id
#m = MovieDocument.documents.get(2)
#m.director = 'Joe Johnston'
#m.save()

#Get all movies
#ms = MovieDocument.documents.all()

#Get the first 10 spielberg's movies
#ms = MovieDocument.documents.q(Q('text', 'spielberg'))[:10]