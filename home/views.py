from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.html import strip_tags
from django.shortcuts import reverse
from django.conf import settings
from django.core.paginator import Paginator

from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

from .forms import SearchByNameForm
from .models import PlayerSearches

from pathlib import Path

import requests
import json
import shutil
import re
# Create your views here.

class HomeView(View):
    
    template_name = 'home/home.html'
    
    def get(self, request, *args, **kwargs):
        
        form = SearchByNameForm()
        
        players = PlayerSearches.objects.all().order_by('-search_count')[:3]
        
        players_dict = {}
                
        for player in players:
           players_dict[player.player] = {
               'url': f"/static/player_imgs/{player.player.split()[0]}_{player.player.split()[1]}.png",
               'searches': player.search_count
           }
                       
        if 'search' in request.GET:
            
            player_name = strip_tags(request.GET['player_name'])
            
            return HttpResponseRedirect(reverse('home:player_detail', args=(player_name,)))
        
        context = {
            'players': players_dict,
            'form': SearchByNameForm
        }
        
        return render(request, self.template_name, context=context)

class PlayerDetail(View):
    
    template_name = 'home/player_detail.html'
    
    def get(self, request, *args, **kwargs):
        
        players_dict_with_stats = {}
        
        players_dict = players.get_players()
        
        player_to_get = [player for player in players_dict if player['full_name'] == kwargs['search_string']][0]
            
        if player_to_get:
            player_obj_search = PlayerSearches.objects.filter(player=player_to_get['full_name'])
                        
            if player_obj_search:
                current_search_count = player_obj_search[0].search_count
                player_obj_search.update(search_count = current_search_count + 1)
            else:
                PlayerSearches.objects.create(player=player_to_get['full_name'], search_count=1)
                
        player_stats = playercareerstats.PlayerCareerStats(player_id=player_to_get['id'], per_mode36='Totals')
        
        player_stats_career = json.loads(player_stats.get_json())['resultSets'][1]
                    
        players_dict_with_stats[player_to_get['full_name']] = player_stats_career['rowSet'][0]
        
        player_first_name = player_to_get['first_name']
        player_last_name = player_to_get['last_name']
        
        url = f'https://nba-players.herokuapp.com/players/{player_last_name}/{player_first_name}'
        
        url_player_stats = f'https://nba-players.herokuapp.com/players-stats/{player_last_name}/{player_first_name}'
           
        api_call = requests.get(url_player_stats)
        
        team_name = api_call.json()['team_name']

        dict_of_player_stats = {
            'ppg': api_call.json()['points_per_game'],
            'fgp': api_call.json()['field_goal_percentage'],
            'ftp': api_call.json()['free_throw_percentage'],
            'tpp': api_call.json()['three_point_percentage'],
            'rpg': api_call.json()['rebounds_per_game'],
            'apg': api_call.json()['assists_per_game'],
            'spg': api_call.json()['steals_per_game'],
            'bpg': api_call.json()['blocks_per_game'],
            'tpg': api_call.json()['turnovers_per_game'],
            'per': api_call.json()['player_efficiency_rating']
        }   
                  
        my_file = Path(settings.STATIC_URL + f'player_imgs/{player_first_name}_{player_last_name}.png')
        
        if not my_file.exists():
                
            api_call = requests.get(url)
    
            file = open(f"static/player_imgs/{player_first_name}_{player_last_name}.png", "wb")
            file.write(api_call.content)
            file.close()
        
        img_url = settings.STATIC_URL + f"player_imgs/{player_first_name}_{player_last_name}.png"
                
        to_remove = ['PLAYER_ID', 'LEAGUE_ID', 'Team_ID']
        
        for to in to_remove:
            player_stats_career['headers'].remove(to)
        
        for i in range(3):
            players_dict_with_stats[player_to_get['full_name']].pop(i)
        
        context = {
            'player': player_to_get,
            'url': img_url,
            'stats': players_dict_with_stats,
            'headers': player_stats_career['headers'],
            'team': team_name,
            'player_season_stats': dict_of_player_stats
        }
        
        return render(request, self.template_name, context=context)

class InactiveSearch(View):
    
    template_name = 'home/archive_search.html'
    
    def get(self, request, *args, **kwargs):
        
        players_dict = players.get_players()

        refined_players = []
    
        for player in players_dict:
            if player['is_active'] == False:
                refined_players.append(player)

        paginator = Paginator(refined_players, 60)
        
        page_number = request.GET.get('page')
        
        page_obj = paginator.get_page(page_number)
        
        context = {
            'players': page_obj,
            'paginator': paginator,
            'range': len(refined_players)
        }
        
        return render(request, self.template_name, context=context)
        
