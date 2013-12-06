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
        
    def test_state_label(self):
        chain = markov.Chain()
        state = chain.new_state('label1')
        self.assertEqual(state, chain.get_state('label1'))

    def test_unqiue_state_labels(self):
        chain = markov.Chain()
        state = chain.new_state('label1')
        with self.assertRaises(ValueError):
            chain.new_state('label1')

    def test_get_state_nonexistent(self):
        chain = markov.Chain()
        self.assertEquals(None, chain.get_state('label1'))

    def test_set_transition(self):
        chain = markov.Chain()
        state = chain.new_state()
        state2 = chain.new_state()
        chain.set_transition(state, state2, 0.5)
        self.assertEqual(0.5, chain.matrix[1,0])

    def test_get_transition(self):
        chain = markov.Chain()
        state = chain.new_state()
        state2 = chain.new_state()
        chain.set_transition(state, state2, 0.5)
        trans = chain.get_transition(state, state2)
        self.assertAlmostEqual(0.5, trans)

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
        
    def test_end_states(self):
        chain = markov.Chain()
        start = chain.new_state('start')
        end = chain.new_state('end')
        chain.set_transition(start, end, 0.05)
        end_states = chain.get_end_states()
        self.assertEqual(1, len(end_states))
        self.assertTrue(end in end_states)

    def test_end_states_split(self):
        """
        Test that if a chain contains multiple end states
        all are reported
        """
        chain = markov.Chain()
        start = chain.new_state('start')
        end1 = chain.new_state('end1')
        end2 = chain.new_state('end2')
        chain.set_transition(start, end1, 0.05)
        chain.set_transition(start, end2, 0.05)
        end_states = chain.get_end_states()
        self.assertEqual(2, len(end_states))
        self.assertTrue(end1 in end_states)
        self.assertTrue(end2 in end_states)
        
    def test_is_absorbing_state(self):
        chain = markov.Chain()
        start = chain.new_state('start')
        end = chain.new_state('end')
        chain.set_transition(start, end, 0.05)
        self.assertEqual(True, chain._is_absorbing_state(end))
        self.assertEqual(False, chain._is_absorbing_state(start))
    
    def test_is_absorbing_true(self):
        chain = markov.Chain()
        start = chain.new_state('start')
        end = chain.new_state('end')
        chain.set_transition(start, end, 0.05)
        self.assertEquals(True, chain.is_absorbing())

    def test_is_absorbing_true_deep(self):
        chain = markov.Chain()
        empty = chain.new_state('empty')
        h = chain.new_state('h')
        ht = chain.new_state('ht')
        hth = chain.new_state('hth')
        chain.set_transition(empty, h, 0.50)
        chain.set_transition(h, ht, 0.50)
        chain.set_transition(ht, hth, 0.50)
        chain.set_transition(ht, empty, 0.50)
        self.assertEqual(True, chain.is_absorbing())

    def test_is_absorbing_false(self):
        chain = markov.Chain()
        one = chain.new_state('one')
        two = chain.new_state('two')
        chain.set_transition(one, two, 0.05)
        chain.set_transition(two, one, 0.05)
        self.assertEqual(False, chain.is_absorbing())
        
    def test_get_absorbing_probabilities(self):
        chain = markov.Chain()
        empty = chain.new_state('empty')
        h = chain.new_state('h')
        t = chain.new_state('t')
        tt = chain.new_state('tt')
        chain.set_transition(empty, h, 0.50)
        chain.set_transition(empty, t, 0.50)
        chain.set_transition(t, tt, 0.50)
        chain.set_transition(t, h, 0.50)
        probabilities = chain.get_absorbing_probabilities()
        self.assertEqual(0.75, probabilities[empty][h])
        self.assertEqual(0.25, probabilities[empty][tt])
        self.assertEqual(0.50, probabilities[t][tt])
        self.assertEqual(0.50, probabilities[t][h])

        
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
