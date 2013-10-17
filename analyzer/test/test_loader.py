import unittest
import analyzer.analyze as analyze
import analyzer.loader as loader

player_lookup = {}
player_lookup['a'] = 'a'
player_lookup['b'] = 'b'
player_lookup['c'] = 'c'
player_lookup['d'] = 'd'

class TestZipList(unittest.TestCase):
    def test_singles(self):
        zipped = loader.zip_lists(['a'],['b'])
        self.assertEqual(['a','b'], zipped)
    def test_doubles(self):
        zipped = loader.zip_lists(['a','c'],['b','d'])
        self.assertEqual(['a','b','c','d'], zipped)
    def test_first_long(self):
        zipped = loader.zip_lists(['a','c'],['b'])
        self.assertEqual(['a','b','c'], zipped)
    def test_second_long(self):
        zipped = loader.zip_lists(['a'],['b','d'])
        self.assertEqual(['a','b','d'], zipped)

class TestPlayersFromMatch(unittest.TestCase):
    def test_partial_ordering(self):
        match = {}
        match['winners'] = ['a']
        match['losers'] = ['b']
        self.assertEqual(['a','b'], loader.players_from_match(match))

    def test_total_ordering(self):
        match = {}
        match['players'] = ['a','b']
        self.assertEqual(['a','b'], loader.players_from_match(match))

class TestJsonToMatch(unittest.TestCase):
    def test_unordered_default(self):
        match_json = {}
        match_json['winners'] = ['a','c']
        match_json['losers'] = ['b','d']
        match = loader.json_to_match(player_lookup, match_json)
        self.assertEqual("unordered", match.order)
        
    def test_unordered(self):
        match_json = {}
        match_json['winners'] = ['a','c']
        match_json['losers'] = ['b','d']
        match_json['ordered'] = False
        match = loader.json_to_match(player_lookup, match_json)
        self.assertEqual("unordered", match.order)
        
    def test_partial_order(self):
        match_json = {}
        match_json['winners'] = ['a','c']
        match_json['losers'] = ['b','d']
        match_json['ordered'] = True
        match = loader.json_to_match(player_lookup, match_json)
        self.assertEqual("partial", match.order)

    def test_total_order(self):
        match_json = {}
        match_json['players'] = ['a','b','c','d']
        match_json['winning-team'] = 0
        match = loader.json_to_match(player_lookup, match_json)
        self.assertEqual("partial", match.order)
        
    def test_winning_team_partial_order(self):
        match_json = {}
        match_json['winners'] = ['a','c']
        match_json['losers'] = ['b','d']
        match_json['ordered'] = True
        match = loader.json_to_match(player_lookup, match_json)
        self.assertEqual(0, match.winning_team)

    def test_total_order(self):
        match_json = {}
        match_json['players'] = ['a','b','c','d']
        match_json['winning-team'] = 1
        match = loader.json_to_match(player_lookup, match_json)
        self.assertEqual(1, match.winning_team)
        
    def test_foul_partial_order(self):
        match_json = {}
        match_json['winners'] = ['a','c']
        match_json['losers'] = ['b','d']
        match_json['ordered'] = True
        match_json['foul-end'] = True
        match = loader.json_to_match(player_lookup, match_json)
        self.assertEqual(True, match.foul_end)

    def test_foul_total_order(self):
        match_json = {}
        match_json['players'] = ['a','b','c','d']
        match_json['winning-team'] = 0
        match_json['foul-end'] = True
        match = loader.json_to_match(player_lookup, match_json)
        self.assertEqual(True, match.foul_end)

class TestJsonToMatches(unittest.TestCase):
    def test_two_matches(self):
        match1_json = {}
        match1_json['winners'] = ['a','c']
        match1_json['losers'] = ['b','d']
        match1_json['ordered'] = True
        match2_json = {}
        match2_json['winners'] = ['b','d']
        match2_json['losers'] = ['a','c']
        match2_json['ordered'] = True
        matches_json = [match1_json, match2_json]
        matches = loader.json_to_matches(matches_json)
        self.assertEqual(2, len(matches))
        # player a is the same in both matches
        self.assertEqual(matches[0].players[0], matches[1].players[1])
        # player a does not equal player b
        self.assertNotEqual(matches[0].players[0], matches[0].players[1])
