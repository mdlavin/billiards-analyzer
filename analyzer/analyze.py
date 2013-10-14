import pymc as pm
import markov
import math
import itertools
import functools

class Match(object):
    def __init__(self, players, winning_team, order="unordered"):
        self.order = order
        self.players = players
        self.winning_team = winning_team

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


def generate_orderings(winners, losers, partial=False):
    results = []
    winner_orderings = []
    loser_orderings = []
    if not partial:
        winner_orderings = itertools.permutations(winners)
        loser_orderings = itertools.permutations(losers)
        all_pairings = itertools.product(winner_orderings, loser_orderings)
        for (winners,losers) in all_pairings:
            results.append( (zip_lists(winners, losers), 0) )
            results.append( (zip_lists(losers, winners), 1) )
    else:
        players = zip_lists(winners, losers)
        for n in range(len(players)):
            results.append( (players[n:] + players[:n] , n % 2) )

    return results

def match_eval_markov_unordered(winners, losers):
    return _match_eval_markov_unordered(winners, losers, False)

def match_eval_markov_partial_ordered(winners, losers):
    return _match_eval_markov_unordered(winners, losers, True)

def _match_eval_markov_unordered(winners, losers, partial):
    if len(winners) != len(losers):
        raise ValueError("The number of winners and losers must be the same")
        
    count=0
    total=0
    
    orderings = generate_orderings(winners, losers, partial=partial)
    for (players, winning_team) in orderings:
        count += 1
        total+=match_eval_markov_total(players, winning_team)

    return total/count

def match_eval_markov(players, winning_team, order):
    if order == "total":
        return match_eval_markov_total(players, winning_team)
    else:
        teams = [[],[]]
        for i in range(len(players)):
            teams[i % 2].append(players[i])
            
        winners = teams[winning_team]
        losers = teams[(winning_team + 1) % 2]
        if order == "unordered":
            return match_eval_markov_unordered(winners, losers)
        else:
            return match_eval_markov_partial_ordered(winners, losers)

def build_markov_chain(players, winning_team):
    if len(players) % 2 != 0:
        raise ValueError("The number of players must be even")

    if winning_team != 0 and winning_team != 1:
        raise ValueError("The winning_team must be either 0 or 1 " +
                         "but was " + str(winning_team))

    chain = markov.Chain()
    winners_win = chain.new_state('winners_win')
    losers_win = chain.new_state('losers_win')
    for player_num in range(len(players)):
        chain.new_state( (player_num, 0, 0) )

    for i in range(len(players)):
        next_player_index = (i+1) % len(players)
        next_player_state = chain.get_state( (next_player_index, 0, 0) )
        chance_of_win = players[i]
        chance_of_miss = 1. - chance_of_win
        player_state = chain.get_state( (i, 0, 0) )
        chain.set_transition(player_state, 
                             next_player_state,
                             chance_of_miss)

        if i % 2 == winning_team:
            end_state = winners_win
        else:
            end_state = losers_win
        chain.set_transition(player_state, end_state, chance_of_win)
    
    return chain

def match_eval_markov_total(players, winning_team):
    chain = build_markov_chain(players, winning_team)
    winners_win_state = chain.get_state('winners_win')
    player_0_start = chain.get_state( (0, 0, 0) )
    result = chain.steady_state(player_0_start)
    return result[winners_win_state]

def all_matches(matches):
    match_vars = []
    
    for i in range(0,len(matches)):
        match=matches[i]
        match_name = 'match_%i' % i

        parents = {'players': match.players,
                   'winning_team': match.winning_team,
                   'order': match.order}
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


