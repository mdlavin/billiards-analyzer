import pymc as pm
import markov
import math
import itertools
import functools
import collections

class Match(object):
    def __init__(self, players, winning_team, order="unordered",
                 foul_end=False):
        self.order = order
        self.players = players
        self.winning_team = winning_team
        self.foul_end = foul_end

        # If there are only two players then they are at least partially
        # ordered
        if order == "unordered" and len(players) == 2:
            self.order = "partial"

def zip_lists(list_a, list_b):
    result = []
    n = max(len(list_a), len(list_b))
    for i in range(n):
        if i < len(list_a):
            result.append(list_a[i])
        if i < len(list_b):
            result.append(list_b[i])
    return result

def reorder(players, winning_team, order_variation):
    # For odd orderings, the winning team's position changes
    if order_variation % 2 != 0:
        winning_team = (winning_team + 1) % 2

    if len(players) % 2 != 0:
        raise ValueError("There must be an even number of players")

    if len(players) > 4:
        raise ValueError("More than 4 players is not currently supported")

    if order_variation == 0:
        return (players, winning_team)
    
    if order_variation < len(players):
        deque = collections.deque(players)
        deque.rotate(order_variation)
        return (list(deque), winning_team)

    if len(players) <= 2:
        raise ValueError("There are only two orderings for two player matches")

    temp_players = list(players)
    temp_players[0] = players[2]
    temp_players[2] = players[0]
    
    if order_variation >= len(players) * 2:
        raise ValueError("There are only eight possible orderings with " +
                         "four players")

    deque = collections.deque(temp_players)
    deque.rotate(order_variation-len(players))
    return (list(deque), winning_team)

    
def match_eval_markov_unordered(players, winning_team, foul_end):
    orderings = range(len(players) * 2)
    return _match_eval_markov(players, winning_team, orderings, foul_end)

def match_eval_markov_partial_ordered(players, winning_team, foul_end):
    orderings = range(len(players))
    return _match_eval_markov(players, winning_team, orderings, foul_end)

def _match_eval_markov(players, winning_team, orderings, foul_end):
    count=0
    total=0
    
    for ordering in orderings:
        total += match_eval_markov(players, winning_team, ordering, foul_end)
        count += 1

    return total/count

def match_eval_markov(players, winning_team, order, foul_end):
    (players, winning_team) = reorder(players, winning_team, order)
    return match_eval_markov_total(players, winning_team, foul_end)
    
def value(v):
    if isinstance(v, pm.Variable):
        return v.value
    else:
        return v


def build_markov_chain(players, winning_team):
    if len(players) % 2 != 0:
        raise ValueError("The number of players must be even")

    if winning_team != 0 and winning_team != 1:
        raise ValueError("The winning_team must be either 0 or 1 " +
                         "but was " + str(winning_team))

    chain = markov.Chain()
    winners_win = chain.new_state('winners_win')
    losers_win = chain.new_state('losers_win')
    winners_win_by_foul = chain.new_state('winners_win_by_foul')
    losers_win_by_foul = chain.new_state('losers_win_by_foul')
    for player_num in range(len(players)):
        chain.new_state( (player_num, 0, 0) )

    for i in range(len(players)):
        next_player_index = (i+1) % len(players)
        next_player_state = chain.get_state( (next_player_index, 0, 0) )
        chance_of_win = value(players[i]['sink'])
        chance_of_foul_end = value(players[i]['foul_end'])
        chance_of_miss = 1. - chance_of_win - chance_of_foul_end
        player_state = chain.get_state( (i, 0, 0) )
        chain.set_transition(player_state, 
                             next_player_state,
                             chance_of_miss)

        if i % 2 == winning_team:
            end_state = winners_win
            foul_end_state = losers_win_by_foul
        else:
            end_state = losers_win
            foul_end_state = winners_win_by_foul
        chain.set_transition(player_state, end_state, chance_of_win)
        chain.set_transition(player_state, foul_end_state, chance_of_foul_end)
    
    return chain

def sum_less_than_one(vars):
    if sum(vars) <= 1:
        return 0.0
    else:
        return -pm.inf

def match_eval_markov_total(players, winning_team, foul_end):
    chain = build_markov_chain(players, winning_team)
    if foul_end:
        winners_win_state = chain.get_state('winners_win_by_foul')
    else:
        winners_win_state = chain.get_state('winners_win')
    player_0_start = chain.get_state( (0, 0, 0) )
    result = chain.steady_state(player_0_start)
    return result[winners_win_state]

def new_player(name, sink=0.5): 
    player = {}
    player['sink'] = pm.Beta(name + "_sink", alpha=3, beta=3, value=sink)
    player['foul_end'] = pm.Beta(name + "_foul_end", alpha=3,
                                 beta=3, value=0.00000000001)
    vars = player.values()
    player['balance'] = pm.Potential(logp = sum_less_than_one,
                                     name = name + "_balance",
                                     parents = {'vars': vars},
                                     doc = name + "_balance")
        
    return player

def all_matches(matches):
    match_vars = []
    
    for i in range(0,len(matches)):
        match=matches[i]
        match_name = 'match_%i' % i

        if match.order == "unordered":
            order = pm.DiscreteUniform('match_%i_order' % i,
                                       lower=0,
                                       upper=len(match.players)*2 - 1)
        else:
            order = pm.DiscreteUniform('match_%i_order' % i,
                                       lower=0,
                                       upper=len(match.players) - 1)

        parents = {'players': match.players,
                   'winning_team': match.winning_team,
                   'order': order,
                   'foul_end': match.foul_end}
        match_var = pm.Deterministic(eval = match_eval_markov,
                                     doc = match_name,
                                     name = match_name,
                                     parents = parents,
                                     plot=False,
                                     dtype=float);
        
        match_vars.append(match_var)

    return match_vars

def outcomes(match_vars):
    outcome_vars = []
    
    for i in range(0,len(match_vars)):
        outcome_vars.append(pm.Bernoulli('outcome_%i' % i, 
                                         match_vars[i], 
                                         value=[True], 
                                         observed=True, 
                                         plot=False))

    return outcome_vars


