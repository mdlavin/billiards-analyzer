import unittest
import analyzer.analyze as analyze

class TestZipList(unittest.TestCase):
    def test_singles(self):
        zipped = analyze.zip_lists(['a'],['b'])
        self.assertEqual(['a','b'], zipped)
    def test_doubles(self):
        zipped = analyze.zip_lists(['a','c'],['b','d'])
        self.assertEqual(['a','b','c','d'], zipped)
    def test_first_long(self):
        zipped = analyze.zip_lists(['a','c'],['b'])
        self.assertEqual(['a','b','c'], zipped)
    def test_second_long(self):
        zipped = analyze.zip_lists(['a'],['b','d'])
        self.assertEqual(['a','b','d'], zipped)

class TestReorder(unittest.TestCase):
    def test_reorder_two(self):
        self.assertEquals((['a','b'],1), analyze.reorder(['a','b'], 1, 0))
        self.assertEquals((['b','a'],0), analyze.reorder(['a','b'], 1, 1))
        
    def test_reorder_two_ordering_too_large(self):
        with self.assertRaises(ValueError):
            analyze.reorder(['a','b'], 0, 2)

    def test_reorder_four(self):
        players = ['a','b','c','d']
        self.assertEquals((['a','b','c','d'],0), analyze.reorder(players, 0, 0))
        self.assertEquals((['d','a','b','c'],1), analyze.reorder(players, 0, 1))
        self.assertEquals((['c','d','a','b'],0), analyze.reorder(players, 0, 2))
        self.assertEquals((['b','c','d','a'],1), analyze.reorder(players, 0, 3))
        self.assertEquals((['c','b','a','d'],0), analyze.reorder(players, 0, 4))
        self.assertEquals((['d','c','b','a'],1), analyze.reorder(players, 0, 5))
        self.assertEquals((['a','d','c','b'],0), analyze.reorder(players, 0, 6))
        self.assertEquals((['b','a','d','c'],1), analyze.reorder(players, 0, 7))
        
    def test_reorder_four_ordering_too_large(self):
        with self.assertRaises(ValueError):
            analyze.reorder(['a','b','c','d'], 0, 8)

class TestMatchEvalMarkovUnordered(unittest.TestCase):
    def test_one_on_one_even(self):
        player1 = analyze.new_player('p1', 0.5)
        player2 = analyze.new_player('p2', 0.5)
        player3 = analyze.new_player('p3', 0.5)
        player4 = analyze.new_player('p4', 0.5)
        players = [player1, player2, player3, player4]
        chance_of_win = analyze.match_eval_markov_unordered(players, 0, False)
        self.assertAlmostEqual(0.5, chance_of_win)

    def test_one_on_one_uneven(self):
        player1 = analyze.new_player('p1', 0.75)
        player2 = analyze.new_player('p2', 0.5)
        player3 = analyze.new_player('p3', 0.75)
        player4 = analyze.new_player('p4', 0.5)
        players = [player1, player2, player3, player4]
        chance_of_win = analyze.match_eval_markov_unordered(players, 0, False)
        self.assertLess(0.5, chance_of_win)

    def test_one_on_one_uneven(self):
        player1 = analyze.new_player('p1', 0.5)
        player2 = analyze.new_player('p2', 0.75)
        player3 = analyze.new_player('p3', 0.5)
        player4 = analyze.new_player('p4', 0.75)
        players = [player1, player2, player3, player4]
        chance_of_win = analyze.match_eval_markov_unordered(players, 0, False)
        self.assertGreater(0.5, chance_of_win)

class TestBuildMarkovChain(unittest.TestCase):
    def test_two_players_even(self):
        player1 = analyze.new_player('p1', 0.5)
        player2 = analyze.new_player('p2', 0.5)
        players = [player1, player2]
        chain = analyze.build_markov_chain(players, 0)
        p1_state = chain.get_state( (0,0,0) )
        p1_wins = chain.get_state('winners_win')
        p2_state = chain.get_state( (1,0,0) )
        p2_wins = chain.get_state('losers_win')
        self.assertAlmostEqual(0.5, chain.get_transition(p1_state, p1_wins)) 
        self.assertAlmostEqual(0.5, chain.get_transition(p2_state, p2_wins)) 
        self.assertAlmostEqual(0.5, chain.get_transition(p1_state, p2_state)) 
        self.assertAlmostEqual(0.5, chain.get_transition(p2_state, p1_state)) 

    def test_two_players_uneven(self):
        player1 = analyze.new_player('p1', 0.5)
        player2 = analyze.new_player('p2', 0.75)
        players = [player1, player2]
        chain = analyze.build_markov_chain(players, 0)
        p1_state = chain.get_state( (0,0,0) )
        p1_wins = chain.get_state('winners_win')
        p2_state = chain.get_state( (1,0,0) )
        p2_wins = chain.get_state('losers_win')
        self.assertAlmostEqual(0.5, chain.get_transition(p1_state, p1_wins)) 
        self.assertAlmostEqual(0.75, chain.get_transition(p2_state, p2_wins)) 
        self.assertAlmostEqual(0.5, chain.get_transition(p1_state, p2_state)) 
        self.assertAlmostEqual(0.25, chain.get_transition(p2_state, p1_state)) 
