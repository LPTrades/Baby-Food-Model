# Daily Research Log - 2026-06-08

## Objective
- See if there are any faulty trades on the 20 random examples pulled from a smoke test of [[v1.6]]
- Debug v1.6

## What I Worked On
- [[v1.6]]
- [[v1.7]]
- [[Debugging v1.6]]

## Problems
- Bug 1: Script walks backwards to find the CISD instead of storing candles based on a state. This bug caused open trades to skip any relevant CISD candles for another trade immediately after.
- Bug 2: The FVG search window ran past the CISD range. Trades were entered far after the CISD formed on pullbacks that would form FVGs.
- Bug 3: CISDs are only invalidates on new sessions, a new extreme on the same side is made or a trade is closed. It does not invalidate and look for a new CISD if the opposite side makes a new 5m break.

## Successes
- Through 2021-2026 and 1100+ trades, the average win rate is 51.1% for 09:30-11:00 at 1RR. THATS A POSITIVE WIN FACTOR

## Insights
- This is still barely profitable and needs to hold up against slower years. Building filters based on volatility or structure might help but I will need to do a lot of backtesting to try to come up with ideas.

## Next Steps
- Log all 82 trades for 2026
- Find more bugs if any
- Figure out the distribution of the edge over different RR targets
- Create filters

## Hours Worked
- 2

## Mood / Confidence
- Ecstatic