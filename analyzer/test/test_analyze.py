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

class TestGenerateOrderings(unittest.TestCase):
    def test_one_on_one(self):
        orderings = analyze.generate_orderings(['a'],['b'], False)
        self.assertEquals(2, len(orderings))
        self.assertTrue((['a','b'], 0) in orderings)
        self.assertTrue((['b','a'], 1) in orderings)

    def test_one_on_one_partial(self):
        orderings = analyze.generate_orderings(['a'],['b'], True)
        self.assertEquals(2, len(orderings))
        self.assertTrue((['a','b'], 0) in orderings)
        self.assertTrue((['b','a'], 1) in orderings)

    def test_two_on_two(self):
        orderings = analyze.generate_orderings(['a','b'],['c','d'], False)
        self.assertEquals(8, len(orderings))
        self.assertTrue((['a','c','b','d'],0) in orderings)
        self.assertTrue((['a','d','b','c'],0) in orderings)
        self.assertTrue((['b','c','a','d'],0) in orderings)
        self.assertTrue((['b','d','a','c'],0) in orderings)
        self.assertTrue((['c','a','d','b'],1) in orderings)
        self.assertTrue((['c','b','d','a'],1) in orderings)
        self.assertTrue((['d','a','c','b'],1) in orderings)
        self.assertTrue((['d','b','c','a'],1) in orderings)

    def test_two_on_two_partial(self):
        orderings = analyze.generate_orderings(['a','b'],['c','d'], True)
        self.assertEquals(4, len(orderings))
        self.assertTrue((['a','c','b','d'],0) in orderings)
        self.assertTrue((['b','d','a','c'],0) in orderings)
        self.assertTrue((['c','b','d','a'],1) in orderings)
        self.assertTrue((['d','a','c','b'],1) in orderings)


class TestMatchEvalMarkovUnordered(unittest.TestCase):
    def test_one_on_one_even(self):
        chance_of_win = analyze.match_eval_markov_unordered([0.5],[0.5])
        self.assertAlmostEqual(0.5, chance_of_win)

    def test_one_on_one_uneven(self):
        chance_of_win = analyze.match_eval_markov_unordered([0.75],[0.50])
        self.assertLess(0.5, chance_of_win)

    def test_one_on_one_uneven(self):
        chance_of_win = analyze.match_eval_markov_unordered([0.50],[0.75])
        self.assertGreater(0.5, chance_of_win)
