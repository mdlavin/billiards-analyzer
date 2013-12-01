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

    def test_three_states(self):
        chain = markov.Chain()
        democrat = chain.new_state("democrat")
        republican = chain.new_state("republican")
        independent = chain.new_state("independent")
        democrat_to_republican = sympy.Symbol("democrat_to_republican")
        independent_to_republican = sympy.Symbol("independent_to_republican")
        republican_to_democrat = sympy.Symbol("republican_to_democrat")
        independent_to_democrat = sympy.Symbol("independent_to_democrat")
        republican_to_independent = sympy.Symbol("republican_to_independent")
        democrat_to_independent = sympy.Symbol("democrat_to_independent")
        chain.set_transition(democrat, republican, democrat_to_republican)
        chain.set_transition(independent, republican, independent_to_republican)
        chain.set_transition(republican, democrat, republican_to_democrat)
        chain.set_transition(independent, democrat, independent_to_democrat)
        chain.set_transition(republican, independent, republican_to_independent)
        chain.set_transition(democrat, independent, democrat_to_independent)
        results = chain.steady_state()
        
        vars = {
            democrat_to_republican: sympy.Rational(2,10),
            independent_to_republican: sympy.Rational(3,10),
            republican_to_democrat: sympy.Rational(1,10),
            independent_to_democrat: sympy.Rational(3,10),
            republican_to_independent: sympy.Rational(1,10),
            democrat_to_independent: sympy.Rational(1,10)
        }
        
        self.assertEqual(sympy.Rational(9,28), results[democrat].subs(vars))
        self.assertEqual(sympy.Rational(15,28), results[republican].subs(vars))
        self.assertEqual(sympy.Rational(1,7), results[independent].subs(vars))

