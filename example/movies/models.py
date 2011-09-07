from django.db import models

class Movie(models.Model):
    
    title = models.CharField()
    director = models.CharField()
    