=================================
Solr Search Engine ORM for Django
=================================

Save some movies::

 MovieDocument(id="1", title='Jurassic Park I', director='Steven Spielberg').save()
 MovieDocument(id="2", title='Jurassic Park III', director='Steven Spielberg').save()
 
Get and update::

 m = MovieDocument.documents.get(2)
 m.director = 'Joe Johnston'
 m.save()
 
Get all movies::

 ms = MovieDocument.documents.all()
 
Get the first 10 spielberg's movies::

 ms = MovieDocument.documents.q(Q('text', 'spielberg'))[:10]

Delete a movie::

 m = MovieDocument.documents.get(1)
 m.delete()

Delete all movies::

 MovieDocument.documents.clear()

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

