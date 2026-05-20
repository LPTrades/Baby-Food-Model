# Problem Report - 2026-05-20

## Problem
- The FVG, stop loss and take profit disappears after a new break happens.

## Possible Cause
- After a new break happens, the script deletes the old break. I assume its using the same logic for everything else.

## Attempted Fixes
- [[FVG HighLow detection fix.png]]

## Current Status
- CLOsED