import pymc as pm
import math
import itertools

class Match(object):
    def __init__(self, winners, losers, ordered=False):
        self.winners = winners
        self.losers = losers
        self.ordered = ordered

        # If both winners and loser are just a single person, then they
        # are effectively ordered
        if not isinstance(winners, list) and not isinstance(losers, list):
            self.ordered = True

        if not isinstance(winners, list):
            self.winners = [self.winners]
        if not isinstance(losers, list):
            self.losers = [self.losers]

    def players(self):
        return self.winners + self.losers    

            
def match_win(winners, losers, ordered=False):
    if len(winners) != len(losers):
        raise ValueError("The number of winners and losers must be the same")

    if not ordered:
        count=0
        total=0
        winner_orderings=itertools.permutations(winners)
        loser_orderings=itertools.permutations(losers)
        all_pairings=itertools.product(winner_orderings, loser_orderings)
        for (winners,losers) in all_pairings:
            count += 1
            total+=match_win(list(winners), list(losers), ordered=True)
        return total/count

    winners_first = []

    # Any of the winners might have sunk their first shot
    for sunk in range(0,len(winners)):
        total = 0.0
        for missed in range(0, sunk):
            total += pm.bernoulli_like([0], losers[missed])
            total += pm.bernoulli_like([0], winners[missed])
        total += pm.bernoulli_like([1], winners[sunk])
        winners_first.append(total)

    # Any of the winners might have sunk their second shot
    for sunk in range(0,len(winners)):
        total = 0.0
        # Anybody before the winning hit must have missed 2 shots
        for missed in range(0, sunk):
            total += pm.bernoulli_like([0,0], winners[missed])
            total += pm.bernoulli_like([0,0], losers[missed])
        total += pm.bernoulli_like([0,1], winners[sunk])
        # Anybody after the winning hit must have missed their first shot
        for missed in range(sunk+1, len(winners)):
            total += pm.bernoulli_like([0], winners[missed])
            total += pm.bernoulli_like([0], losers[missed])
        winners_first.append(total)

    losers_first = []

    # Any of the winners might have sunk their first shot
    for sunk in range(0,len(winners)):
        total = 0.0
        for missed in range(0, sunk):
            total += pm.bernoulli_like([0], losers[missed])
            total += pm.bernoulli_like([0], winners[missed])
        total += pm.bernoulli_like([0], losers[sunk])
        total += pm.bernoulli_like([1], winners[sunk])
        losers_first.append(total)

    # Any of the winners might have sunk their second shot
    for sunk in range(0,len(winners)):
        total = 0.0
        # Anybody before the winning hit must have missed 2 shots
        for missed in range(0, sunk):
            total += pm.bernoulli_like([0,0], losers[missed])
            total += pm.bernoulli_like([0,0], winners[missed])
        total += pm.bernoulli_like([0,0], losers[sunk])
        total += pm.bernoulli_like([0,1], winners[sunk])
        # Anybody after the winning hit must have missed 1 shot
        for missed in range(sunk+1, len(winners)):
            total += pm.bernoulli_like([0], losers[missed])
            total += pm.bernoulli_like([0], winners[missed])
        losers_first.append(total)
        
        chance_of_winners_first = math.fsum(map(math.exp, winners_first))
        chance_of_losers_first = math.fsum(map(math.exp, losers_first))

        return (chance_of_winners_first + chance_of_losers_first)/2.0

def all_matches(matches):
    match_vars = []
    
    for i in range(0,len(matches)):
        match=matches[i]
        match_name = 'match_%i' % i
        match_var = pm.Deterministic(eval = match_win,
                                     doc = match_name,
                                     name = match_name,
                                     parents = {'winners': match.winners,
                                                'losers': match.losers},
                                     plot=False);
        
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


