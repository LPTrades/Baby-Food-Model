# Experiment - 2026-06-03

## Objective
- 

## Hypothesis
- Last experiment [[v1.5 win rate by time clusters]] revealed Monday and Friday being the best days, while Wednesday and Thursday were the worst days. I suspect this is because expansion days cause losses. By eliminating overnight trends, I hope to see something more even day by day.

## Dataset / Market
- NQ 2021-2026

## Result
==================================================
  OVERNIGHT TREND FILTER — THRESHOLD COMPARISON
==================================================
  Threshold       Trades  Removed   Win %     Exp R     PF      Sim Bal
  ---------------------------------------------------------------------
  None (0.00)       3025        0   45.8%   -0.084R   0.84  $    678.35
  0.60              2003     1022   45.4%   -0.093R   0.83  $  1,417.59
  0.70              2336      689   45.7%   -0.086R   0.84  $  1,194.43
  0.80              2684      341   45.6%   -0.086R   0.84  $    859.12



## Conclusion
- Overnight trends don't influence probability.

## Follow-Up Ideas
- Create a filter to test no trading after post 08:30 moves 'x' amount of points.