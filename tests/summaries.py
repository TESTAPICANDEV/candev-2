from candev import core

s = core.VariableSummarizer('Test variable', [1, 2, 4, 3, 2])
print(s.short_quantitative_summary())
