import simplejson as json
import analyzer.analyze as analyze
import itertools

def zip_lists(list_a, list_b):
    result = []
    n = max(len(list_a), len(list_b))
    for i in range(n):
        if i < len(list_a):
            result.append(list_a[i])
        if i < len(list_b):
            result.append(list_b[i])
    return result

def players_from_match(match):
    if "players" in match:
        return match['players']
    else:
        return zip_lists(match['winners'], match['losers'])

def json_to_match(player_lookup, match):
    players = map(lambda p: player_lookup[p], players_from_match(match))
    if "players" in match:
        winning_team = match['winning-team']
        ordered = "partial"
    else:
        winning_team = 0
        ordered = "unordered"
        if "ordered" in match:
            if match['ordered']:
                ordered = "partial"
            else:
                ordered = "unordered"
            
    if "foul-end" in match:
        foul_end = match['foul-end']
    else:
        foul_end = False
            
    return analyze.Match(players, winning_team, ordered, foul_end)

def json_to_matches(matches_json):
    players_for_each_match = map(players_from_match, matches_json)
    all_player_names = set(itertools.chain(*players_for_each_match))
    player_lookup = {}
    for name in all_player_names:
        player_lookup[name] = analyze.new_player(name)
        
    matches = []
    for match in matches_json:
        newMatch = json_to_match(player_lookup, match)
        matches.append(newMatch)

    return matches
