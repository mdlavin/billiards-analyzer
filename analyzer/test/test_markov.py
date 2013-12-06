import analyzer.markov as markov
import unittest
import abc_markov

class ChainTest(abc_markov.AbstractChainTest, unittest.TestCase):
    
    def _createChain(self):
        return markov.Chain()
    
    def _createDummyTransitionValue(self):
        return 0.5

    def _chanceOfCoinFlip(self):
        return 0.5
        
    def test_steady_state(self):
        chain = markov.Chain()
        city = chain.new_state()
        suburban = chain.new_state()
        chain.set_transition(city, suburban, 0.4)
        chain.set_transition(suburban, city, 0.3)
        results = chain.steady_state()
        self.assertAlmostEqual(0.57142857, results[suburban])
        self.assertAlmostEqual(0.42857143, results[city])
        
    def test_steady_state_2(self):
        chain = markov.Chain()
        city = chain.new_state()
        suburban = chain.new_state()
        chain.set_transition(city, suburban, 0.05)
        chain.set_transition(suburban, city, 0.03)
        start = {}
        start[city] = 0.582
        start[suburban] = 0.418
        results = chain.steady_state(start)
        self.assertAlmostEqual(0.625, results[suburban])
        self.assertAlmostEqual(0.375, results[city])
        
    def test_swap_indicies(self):
        chain = markov.Chain()
        one = chain.new_state('one')
        two = chain.new_state('two')
        chain.set_transition(one, two, 0.12)
        chain.set_transition(two, one, 0.21)
        chain.matrix = chain._fill_in_diagonal_transistions(chain.matrix)
        before0x0 = chain.matrix[0,0]
        before1x1 = chain.matrix[1,1]
        chain._swap_indices(chain.matrix, 0, 1)
        # The old 0x0 value should now be at 1x1
        self.assertEqual(before0x0, chain.matrix[1,1])
        # The old 1x1 value should now be at 0x0
        self.assertEqual(before1x1, chain.matrix[0,0])
