# Problem Report 

## Problem
- Claude isn't interpreting the high and low of a fvg properly.

## Symptoms
- Claude is entering a bullish fvg on its lower end instead of as soon as price comes back into the fvg.

## Possible Cause
- A fvg is a three candle formation, involving candle 1s high/low to form the low/high and candle 3 low/high to form the high/low of the fvg. It might be mixing up these terms.

## Attempted Fixes
- [[FVG High and Low Detection]]

## Current Status
- Closed