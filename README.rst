=================================
Solr Search Engine ORM for Django
=================================

 #Delete all movies
 MovieDocument.documents.clear()

  #Save some movies
  MovieDocument(id="1", title='Jurassic Park I', director='Steven Spielberg').save()
  MovieDocument(id="2", title='Jurassic Park III', director='Steven Spielberg').save()

  #Get and update a movie by id
  m = MovieDocument.documents.get(2)
  m.director = 'Joe Johnston'
  m.save()

  #Get all movies
  ms = MovieDocument.documents.all()

  #Get the first 10 spielberg's movies
  ms = MovieDocument.documents.q(Q('text', 'spielberg'))[:10]

Installation
============
easy_install django-solr


