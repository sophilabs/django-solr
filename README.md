=================================
Solr Search Engine ORM for Django
=================================

Define::

 from djangosolr import documents
 
 class Movie(documents.Document):
     id = documents.IntegerField(primary_key=True)
     title = documents.CharField()
     director = documents.CharField()
     text = TextField()

Define from an existing django model::
  
 from djangosolr import documents
 from myapp import models

 class Movie(documents.Document):
     class Meta:
         model = models.Movie
     

Save some movies::

 Movie(id="1", title='Jurassic Park I', director='Steven Spielberg').save()
 Movie(id="2", title='Jurassic Park III', director='Steven Spielberg').save()

Save many movies at once::
  
 from djangosolr import solr

 solr.save([m1, m2])
 
Get and update::

 m = Movie.documents.get(2)
 m.director = 'Joe Johnston'
 m.save()
 
Get all movies::

 ms = Movie.documents.all()

Get the first 10 Steven Spielberg's movies::

 ms = Movie.documents.q(director__exact='Steven Spielberg').sort('title')[:10]

Get Spielberg's or Johnston's movies::

 ms = Movie.documents.q(Q(text='spielberg') | Q(text='johnston'))

Delete a movie::

 m = Movie.documents.get(1)
 m.delete()

Delete all movies::

 Movie.documents.clear()

Getting It
==========
 
You can get Django Solr by using pip or easy_install::
 
 $ pip install django-solr
 or
 $ easy_install django-solr

Comming Soon
============

* Facet
* More Like This

