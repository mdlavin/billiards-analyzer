class AbstractChainTest(object):

    def _createChain(self):
        raise Exception("_createChain must be implemented")
        
    def _createDummyTransitionValue(self):
        raise Exception("_createDummyTransitionValue must be implemented")

    def _chanceOfCoinFlip(self):
        raise Exception("_chanceOfCoinFlip must be implemented")
    
    def test_init(self):
        chain = self._createChain() 
        self.assertEquals(None, chain.matrix)
        self.assertEquals({}, chain.states)

    def test_first_state(self):
        chain = self._createChain()
        state = chain.new_state()
        self.assertEquals((1,1), chain.matrix.shape)
        self.assertTrue( state in chain.states )
        self.assertEqual(0, chain.states[state])

    def test_second_state(self):
        chain = self._createChain()
        state = chain.new_state()
        state2 = chain.new_state()
        self.assertEquals((2,2), chain.matrix.shape)
        self.assertTrue( state in chain.states )
        self.assertTrue( state2 in chain.states )
        self.assertEqual(0, chain.states[state])
        self.assertEqual(1, chain.states[state2])
        self.assertNotEqual(state, state2)

    def test_state_label(self):
        chain = self._createChain()
        state = chain.new_state('label1')
        self.assertEqual(state, chain.get_state('label1'))

    def test_unqiue_state_labels(self):
        chain = self._createChain()
        state = chain.new_state('label1')
        with self.assertRaises(ValueError):
            chain.new_state('label1')

    def test_get_state_nonexistent(self):
        chain = self._createChain()
        self.assertEquals(None, chain.get_state('label1'))

    def test_set_transition(self):
        chain = self._createChain()
        state = chain.new_state()
        state2 = chain.new_state()
        trans = self._createDummyTransitionValue()
        chain.set_transition(state, state2, trans)
        self.assertEqual(trans, chain.matrix[1,0])

    def test_get_transition(self):
        chain = self._createChain()
        state = chain.new_state()
        state2 = chain.new_state()
        trans = self._createDummyTransitionValue()
        chain.set_transition(state, state2, trans)
        trans_get = chain.get_transition(state, state2)
        self.assertAlmostEqual(trans, trans_get)

    def test_end_states(self):
        chain = self._createChain()
        start = chain.new_state('start')
        end = chain.new_state('end')
        trans = self._createDummyTransitionValue()
        chain.set_transition(start, end, trans)
        end_states = chain.get_end_states()
        self.assertEqual(1, len(end_states))
        self.assertTrue(end in end_states)

    def test_end_states_split(self):
        """
        Test that if a chain contains multiple end states
        all are reported
        """
        chain = self._createChain()
        start = chain.new_state('start')
        end1 = chain.new_state('end1')
        end2 = chain.new_state('end2')
        trans = self._createDummyTransitionValue()
        chain.set_transition(start, end1, trans)
        chain.set_transition(start, end2, trans)
        end_states = chain.get_end_states()
        self.assertEqual(2, len(end_states))
        self.assertTrue(end1 in end_states)
        self.assertTrue(end2 in end_states)

    def test_is_absorbing_true(self):
        chain = self._createChain()
        start = chain.new_state('start')
        end = chain.new_state('end')
        trans = self._createDummyTransitionValue()
        chain.set_transition(start, end, trans)
        self.assertEquals(True, chain.is_absorbing())

    def test_is_absorbing_true_deep(self):
        chain = self._createChain()
        empty = chain.new_state('empty')
        h = chain.new_state('h')
        ht = chain.new_state('ht')
        hth = chain.new_state('hth')
        trans = self._createDummyTransitionValue()
        chain.set_transition(empty, h, trans)
        chain.set_transition(h, ht, trans)
        chain.set_transition(ht, hth, trans)
        chain.set_transition(ht, empty, trans)
        self.assertEqual(True, chain.is_absorbing())

    def test_is_absorbing_false(self):
        chain = self._createChain()
        one = chain.new_state('one')
        two = chain.new_state('two')
        trans = self._createDummyTransitionValue()
        chain.set_transition(one, two, trans)
        chain.set_transition(two, one, trans)
        self.assertEqual(False, chain.is_absorbing())
        
    def test_get_absorbing_probabilities(self):
        chain = self._createChain()
        empty = chain.new_state('empty')
        h = chain.new_state('h')
        t = chain.new_state('t')
        tt = chain.new_state('tt')
        flip = self._chanceOfCoinFlip()
        chain.set_transition(empty, h, flip)
        chain.set_transition(empty, t, flip)
        chain.set_transition(t, tt, flip)
        chain.set_transition(t, h, flip)
        probabilities = chain.get_absorbing_probabilities()
        self.assertEqual(0.75, probabilities[empty][h])
        self.assertEqual(0.25, probabilities[empty][tt])
        self.assertEqual(0.50, probabilities[t][tt])
        self.assertEqual(0.50, probabilities[t][h])
