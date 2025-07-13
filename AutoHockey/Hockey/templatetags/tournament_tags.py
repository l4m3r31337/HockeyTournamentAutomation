from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '0:0')

@register.simple_tag
def get_player_team(table, player_index, game_num):
    return table.get_team_for_player_in_game(player_index, game_num)