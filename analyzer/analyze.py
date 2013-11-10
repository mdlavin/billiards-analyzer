import pymc as pm
import numpy as np
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

def _build_uninitialized_chain(num_players):
    chain = markov.Chain()

    for team_a_balls in range(8):
        chain.new_state( (0, 'win', 0, team_a_balls) )
        chain.new_state( (1, 'win', team_a_balls, 0) )
        for team_b_balls in range(8):
            chain.new_state( (0, 'foul-win', team_a_balls, team_b_balls) )
            chain.new_state( (1, 'foul-win', team_a_balls, team_b_balls) )
            for player_num in range(num_players):
                chain.new_state( (player_num, team_a_balls, team_b_balls) )

    return chain

def _set_state_transitions(players, chain):
    for i in range(len(players)):
        next_player_index = (i+1) % len(players)
        
        chance_of_sink = value(players[i]['sink'])
        chance_of_foul_end = value(players[i]['foul_end'])
        chance_of_miss = 1. - (chance_of_sink + chance_of_foul_end)
        while np.sum([chance_of_sink,
                      chance_of_foul_end, 
                      chance_of_miss],
                     dtype=np.float64) > 1:
            chance_of_miss = chance_of_miss - sys.float_info.epsilon

        for team_a_balls in range(8):
            for team_b_balls in range(8):
                next_player_state = chain.get_state(
                    (next_player_index, team_a_balls, team_b_balls)
                )
                    
                player_state = chain.get_state(
                    (i, team_a_balls, team_b_balls)
                )
                # Create the player miss transition
                chain.set_transition(player_state, 
                                     next_player_state,
                                     chance_of_miss)

                # Create the foul win transition
                foul_end_state = chain.get_state(
                    ((i+1) % 2, 'foul-win', team_a_balls, team_b_balls)
                )
                chain.set_transition(player_state, foul_end_state,
                                     chance_of_foul_end)

                # Create the sink transition
                if i % 2 == 0:
                    if team_a_balls == 0:
                        sink_label = (0, 'win', 0, team_b_balls)
                    else:
                        sink_label = (i, team_a_balls-1, team_b_balls)
                else:
                    if team_b_balls == 0:
                        sink_label = (1, 'win', team_a_balls, 0)
                    else:
                        sink_label = (i, team_a_balls, team_b_balls-1)

                sink_state = chain.get_state(sink_label)
                chain.set_transition(player_state, sink_state, chance_of_sink)


def build_markov_chain(players):
    if len(players) % 2 != 0:
        raise ValueError("The number of players must be even")


    # Create states before the transition probabilities so they'll be ready
    # to reference
    chain = _build_uninitialized_chain(len(players))
    _set_state_transitions(players, chain)
    
    return chain

def sum_less_than_one(vars):
    if sum(vars) <= 1:
        return 0.0
    else:
        return -pm.inf

def _win_states(winning_team, foul_end):
    def _create_state(winning_balls, losing_balls):
        state_label = 'foul-win' if foul_end else 'win'
        if winning_team == 0:
            team_a_balls = winning_balls
            team_b_balls = losing_balls
        else:
            team_a_balls = losing_balls
            team_b_balls = winning_balls
            
        return (winning_team, state_label, team_a_balls, team_b_balls)
        
    for losing_team_balls in range(8):
        if foul_end:
            for winning_team_balls in range(8):
                yield _create_state(winning_team_balls, losing_team_balls)
        else:
            yield _create_state(0, losing_team_balls)
        
            

def match_eval_markov_total(players, winning_team, foul_end):
    if winning_team != 0 and winning_team != 1:
        raise ValueError("The winning_team must be either 0 or 1 " +
                         "but was " + str(winning_team))

    chain = build_markov_chain(players)
    player_0_start = chain.get_state( (0, 0, 0) )

    result = chain.steady_state(player_0_start)
   
    total = 0
    for end_state in _win_states(winning_team, foul_end):
        total += result[chain.get_state(end_state)]
        
    return total

def new_player(name, sink=0.5, foul=1e-10): 
    player = {}
    player['sink'] = pm.Beta(name + "_sink", alpha=3, beta=3, value=sink)
    player['foul_end'] = pm.Beta(name + "_foul_end", alpha=3,
                                 beta=3, value=foul)
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
