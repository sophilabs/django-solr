"""
    Solr Search Engine ORM for Django models*
    
    Create, save, fetch, update and delete:
    <code>
        mv = MovieDocument(title='Jurassic Park', director='Steven Spielberg')
        mv.save()
        
        mv = MovieDocument.docuemnts.get(1)
        
        mv.title = 'Jurassic Park I'
        mv.save()
        
        mv.delete()
    </code>
    
    Search:
    <code>
        MovieDocument.documents.q(Q('jurassic park') & Q('director', 'spielberg'))[:10]
    </code>
    
    *Solr Not Included
"""

__version__ = (0, 0, 2)

from djangosolr.conf import inject_defaults
inject_defaults()
