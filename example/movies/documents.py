from example.movies.models import Movie as MovieDB
from djangosolr.documents import Document, TextField

class Movie(Document):
    
    text = TextField(stored=False)
    
    class Meta:
        model = MovieDB
        type = 'movie'