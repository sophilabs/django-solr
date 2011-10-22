import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'
from example.movies.documents import Movie
from djangosolr.documents import Q

#Save some movies
Movie(id="1", title='Jurassic Park I', director='Steven Spielberg').save()
Movie(id="2", title='Jurassic Park III', director='Steven Spielberg').save()
 
#Get and update
m = Movie.documents.get(2)
m.director = None
m.save()
 
#Get all movies
ms = Movie.documents.all()

#Get the first 10 Steven Spielberg's movies
ms = Movie.documents.q(director__exact='Steven Spielberg').sort('title')[:10]
print ms.count()
for m in ms:
    print m.title

#Get Spielberg's or Johnston's movies
ms = Movie.documents.q(Q(text='spielberg'))
for m in ms:
    print m.title, m.director, m.text

#Delete a movie
m = Movie.documents.get(1)
m.delete()

#Delete all movies
Movie.documents.clear()
