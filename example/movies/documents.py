from example.movies.models import Movie
from djangosolr.documents import Document, TextField

class MovieDocument(Document):
    
    text = TextField()
    
    class Meta:
        model = Movie
        type = 'movie'