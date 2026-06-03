# Problem Report - 2026/06/01

## Problem
- The recent version 1 scripts written by claude fail to work. They are entering on prices that don't exist, 

## Symptoms
- All data the entries are off by ~60 points from where price really is.
- Most of the time there isn't any valid entries remotely close to the time of entry.

## Possible Cause
- It is not because the .csv containing the data is wrong. I checked.
- Claude cannot easily convert a pine script to python, especially when it serves a different purpose.

## Attempted Fixes
- [[Fixing v1.4]]
- Initially 1.5 was giving me no trades. I ran a debug to figure out what part(s) of the model the script isn't getting right and found it wasn't detecting any fvg's.
  ╔══════════════════════════════════════════╗ 
  ║ SETUP FUNNEL DIAGNOSTIC ║ 
  ╠══════════════════════════════════════════╣ 
  ║ 5m swing breaks (long) 1,925 ║ 
  ║ 5m swing breaks (short) 1,988 ║ 
  ║ Total breaks 3,913 ║ 
  ╠══════════════════════════════════════════╣ 
  ║ CISD ≥2 candles (long) 21,533 ║ 
  ║ CISD ≥2 candles (short) 23,180 ║ 
  ╠══════════════════════════════════════════╣ 
  ║ FVG found in CISD (long) 0 ║ 
  ║ FVG found in CISD (short) 2 ║ 
  ╠══════════════════════════════════════════╣ 
  ║ CISD confirmed (long) 1,362 ║ 
  ║ CISD confirmed (short) 1,364 ║ 
  ║ Confirmed, no FVG (long) 1,362 ║ 
  ║ Confirmed, no FVG (short) 1,362 ║ 
  ╠══════════════════════════════════════════╣ 
  ║ ENTRIES (long) 0 ║ ║ ENTRIES (short) 2 ║ 
  ║ ENTRIES (total) 2 ║ 
  ╚══════════════════════════════════════════╝
## Current Status
- Open