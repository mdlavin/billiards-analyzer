import analyzer.markov_symbolic as markov
import unittest
import sympy

class SymbolicChainTest(unittest.TestCase):

    def setUp(self):
        self.chain = markov.Chain()
        self.city = self.chain.new_state("city")
        self.suburban = self.chain.new_state("suburban")
        self.sub_to_city = sympy.Symbol("suburb_to_city")
        self.city_to_sub = sympy.Symbol("city_to_suburb")
        self.chain.set_transition(self.suburban, self.city, self.sub_to_city)
        self.chain.set_transition(self.city, self.suburban, self.city_to_sub)
        self.results = self.chain.steady_state()
        
    
    def test_steady_state(self):
        vals = {
            self.sub_to_city: 0.3,
            self.city_to_sub: 0.4
        }

        steady_state_city = self.results[self.city].subs(vals)
        steady_state_suburban = self.results[self.suburban].subs(vals)
        self.assertAlmostEqual(0.57142857, steady_state_suburban)
        self.assertAlmostEqual(0.42857143, steady_state_city)
        
    def test_steady_state_2(self):
        vals = {
            self.sub_to_city: 0.03,
            self.city_to_sub: 0.05
        }
        steady_state_city = self.results[self.city].subs(vals)
        steady_state_suburban = self.results[self.suburban].subs(vals)
        self.assertAlmostEqual(0.625, steady_state_suburban)
        self.assertAlmostEqual(0.375, steady_state_city)
