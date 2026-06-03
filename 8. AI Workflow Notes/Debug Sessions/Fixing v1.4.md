# AI Development Log - 2026/06/01
## Objective  
- Fix v1.4
- Start from scratch and use one prompt to describe the rules, functions and outputs.
  
## Important Prompt  
- Prompt 1
```
Build a python Script strategy. Follow the rules below exactly.

# Long Setup (Vice Versa for Shorts)
1. A 5-minute swing low is broken.
2. After the swing low is broken, begin looking for a long setup on the 1-minute chart.
3. A long entry occurs immediately at market when:
    - A valid bullish CISD forms.    
    - A valid bullish FVG exists within the active CISD range.   
4. Stop loss is placed at the highest close of the bullish CISD range.
5. Take profit is placed at 1RR. 
6. Reverse all logic for shorts. 

# Swing Logic
## A 5m swing low consists of:
- three 5m candles making a low, lower low, and higher low
- All of these candles are consecutive
- The swing low level is the second candle's low, the lower low
## A 5m swing high consists of:
- three 5m candles making a high, higher high, and lower high
- All of these candles are consecutive
- The swing high level is the second candle's high, the higher high
## The bearish break happens:
- Immediately when price trades beneath the recent 5m swing low
- Do not wait until the current 5m candle closes
## The bullish break happens:
- Immediately when price trades above the recent 5m swing high
- Do not wait until the current 5m candle closes



# CISD Specifications

## Bullish CISD (for longs)

- The CISD range consists of more than one consecutive bearish candle.
- The high of the CISD range is the open of the first bearish candle in the consecutive bearish sequence.
- A bullish CISD forms when price closes above the high of the CISD range. 
- The stop loss is placed at the lowest closing price among all candles in the active CISD range.
- The active CISD range is always the most recent sequence of consecutive bearish candles.
- If a new lower low is made by consecutive bearish candles, the CISD range must update to include the new candles.

## Bearish CISD (for shorts)

- The CISD range consists of more than one consecutive bullish candle.
- The low of the CISD range is the open of the first bullish candle in the consecutive bullish sequence.
- A bearish CISD forms when price closes below the low of the CISD range.
- The stop loss is placed at the highest closing price among all candles in the active CISD range.
- The active CISD range is always the most recent sequence of consecutive bullish candles.
- If a new higher high is made by consecutive bullish candles, the CISD range must update to include the new candles.

# FVG Specifications

## Bearish FVG

### A bearish FVG consists of three candles:
- Candle 1 low = FVG high.
- Candle 3 high = FVG low.
- Candle 2 is a displacement candle that creates a gap between Candle 1 low and Candle 3 high.  

## Bullish FVG

### A bullish FVG consists of three candles:
- Candle 1 high = FVG low.
- Candle 3 low = FVG high.  
- Candle 2 is a displacement candle that creates a gap between Candle 1 high and Candle 3 low.   

# CISD and FVG Rules:

- Only Candle 2 is required to belong to the active consecutive bullish candle sequence that forms the CISD range.   
- Store only the first bullish FVG found within the active CISD range.
- If the CISD range extends with a new higher high, discard the previously stored FVG and rescan the updated CISD range.
- Store the earliest valid bullish FVG found in the updated range.

# Entry Requirements

- A trade is entered immediately upon a CISD confirmation if a valid stored FVG exists within the active CISD range.
- No retracement into the FVG is required.
- The FVG is only a qualification filter for the setup.

## For an entry to occur:
- The FVG must exist within the active CISD range. 
- Candle 2 of the FVG must be part of the consecutive candles forming the active CISD range.  
- If no valid FVG exists within the active CISD range, no trade is taken.  

# Trade Management
- Only one setup may be active at a time.
- No additional setups may be evaluated until a fresh 5-minute swing high or swing low is broken.
- Remain in the setup unless SL, TP or another trade is entered.

# Time Rules
- Only search for new setups between 9:30 AM and 12:00 AM. 
- New entries may only occur during this time window.
- Existing trades must remain active after 12:00 AM until TP or SL, or 15:45 is reached.
- Do not force-close trades because the session window has ended.

# Output requirements

## Basic statisitc (saved on a .txt file)
- Pull data by year and then all years combined
- Win/Loss
- Win %
- Profit factor
- Expectancy (average r per trade)
- Longest losing streak
- Longest winning streak
- simulated % risking 1% with $10 000

## Visual graph of equity curve (saved as a file)
- X axis: month by month
- Y axis: Account balance starting
- Can show negative values on Y axis

## 20 random examples from 2026 (saved on a .csv file)
- Time of entry
- W/L
- CISD level
- Time of the FVG's candle 2
- Entry price
- TP price
- SL price

## Other
- Input a yes or know answer to close the program
- Input 5m data (by default its called 5m.csv)
- Input 1m data( by default its called 1m.csv)
- Input years to backtest ( by default 2021, 2022, 2023, 2024, 2025, 2026 | input example: 2022,2023,2025)
- Input session time (by default 09:30 to 12:00)
- Input rr (by default 1rr)
- All 5m and 1m data is found in C:\tradingProject\Data
- All outputs should be saved in a new folder called "backtestResults_YYYYtoYYYY
```
  - Claude ran a debug test to see what the problem is. 2 trades were found from the script.
  - I pasted my pine script to compare it and see if maybe Claude was not understanding the fvg and CISD concept.
## Claude Response Summary  
- Initially 1.5 was giving me no trades. I ran a debug to figure out what part(s) of the model the script isn't getting right and found it wasn't detecting any fvg's.
-  The output for the debug test is below. It appears there is a problem with fvg detection.
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
  - The three bugs Claude found:
    - **Bug 1 — FVG direction was completely backwards** For longs (bearish CISD) we need a **bearish FVG**: `c1.low > c3.high`. We were checking `c3.low > c1.high` which is a bullish FVG. Opposite direction, almost never matched inside a bearish run.
    - **Bug 2 — CISD range only updates on new lower low** Pine only extends the range when `bar.low < cisd_range_low`. We were updating it on every candle. This changes which FVG gets stored.
    - **Bug 3 — FVG scan window extended by +5 bars** Pine uses `cisd_end_idx + 5` as the upper bound for candle 2. Gives the scan room to catch FVGs that form just after the last CISD candle closes.
- Final script, I verified the outputs and made sure the model was being tested properly. It is. [[v1.5 (CISD + IFVG)]]
## What I Learned  
-  Don't try to go from a script with the model serving one function to another script with the model serving a different function directly. Build both separately and then compare its logic.
  
## Final Decision  
-  Updated to new version
  
## Related Files  
- [[v1.5 (CISD + IFVG)]]
- [[Versions 1.0 to 1.4 do not work [CLOSED]]]