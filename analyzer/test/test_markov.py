import analyzer.markov as markov
import unittest

class ChainTest(unittest.TestCase):
    
    def test_init(self):
        chain = markov.Chain()
        self.assertEquals(None, chain.matrix)
        self.assertEquals({}, chain.states)

    def test_first_state(self):
        chain = markov.Chain()
        state = chain.new_state()
        self.assertEquals((1,1), chain.matrix.shape)
        self.assertTrue( state in chain.states )
        self.assertEqual(0, chain.states[state])

    def test_second_state(self):
        chain = markov.Chain()
        state = chain.new_state()
        state2 = chain.new_state()
        self.assertEquals((2,2), chain.matrix.shape)
        self.assertTrue( state in chain.states )
        self.assertTrue( state2 in chain.states )
        self.assertEqual(0, chain.states[state])
        self.assertEqual(1, chain.states[state2])
        self.assertNotEqual(state, state2)
        
    def test_set_transition(self):
        chain = markov.Chain()
        state = chain.new_state()
        state2 = chain.new_state()
        chain.set_transition(state, state2, 0.5)
        self.assertEqual(0.5, chain.matrix[1,0])

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
