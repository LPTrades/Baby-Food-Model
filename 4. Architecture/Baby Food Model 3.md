# Baby Food Model 3

## Core Logic
- 5m swing liquidity
- Break of swing
- First associated 1m FVG
- Quick 2rr trades
- Reversal model
## Stop loss logic
- Place stop loss on the lowest low that formed after taking out the last 5m swing creating a break.

## Current Progress
- Swing detection complete
- FVG association complete

## Next Priorities
- Setup times for swing detection [[3. Problems/Swing Detection Timing]]
- Entry visualization
- SL logic
- TP logic

## What does success look like
- Model able to execute orders on its own
- 6 months of live testing with positive returns
- Ability to test the model against old data
- Ability to improve the model by collecting data on losing and winning trades

## Visuals
![[20260519 v0.4 visual.png]]