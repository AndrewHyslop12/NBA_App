from django.db import models

# Create your models here.
class PlayerSearches(models.Model):
    
    player = models.CharField(max_length=100)
    search_count = models.IntegerField()
    
    def __str__(self):
        return self.player