import unittest

from candev import core

s = core.VariableSummarizer('Test variable', [1, 2, 4, 3, 2])
print(s.short_quantitative_summary())

class VariableSummarizerTests(unittest.TestCase):
    def test_long_with_reversal(self):
        s = core.VariableSummarizer('Long test variable', [1, 2, 3, 2, 5, 6, 7, 6])
        observed = s.long_quantitative_summary()
        self.assertTrue(
            'following 3 consecutive months' in observed,
            msg=observed
        )

        s = core.VariableSummarizer('Long test variable', [1, 0.5, 3, 4, 5, 6, 7, 6])
        observed = s.long_quantitative_summary()
        self.assertTrue(
            'following 5 consecutive months' in observed,
            msg=observed
        )

if __name__ == '__main__':
    unittest.main()
