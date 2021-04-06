from django.contrib import admin
from django.urls import path

from .views import HomeView, PlayerDetail, InactiveSearch

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('player-detail/<str:search_string>', PlayerDetail.as_view(), name='player_detail'),
    path('archive-search/', InactiveSearch.as_view(), name='inactive_search')
]
