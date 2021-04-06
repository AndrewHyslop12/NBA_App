from django.contrib import admin
from .models import PlayerSearches

# Register your models here.
@admin.register(PlayerSearches)
class PlayerSearchAdmin(admin.ModelAdmin):
    
    list_display = ('player', 'search_count')