# AI Development Log - 2026-05-30
## Objective  
-  Refine the pine script by prompting it once with clearer instructions
  
## Important Prompt  
-  Prompt I gave to ChatGPT
  build me a model using this script as foundation Long setup (vice versa for shorts) 1. 5m swing low is broken —> Start looking on 1m chart for setup 2. Entry is at market on formation of two concepts: - CISD - bearish fvg 3. Stop loss is at the lowest close of the ‘CISD range’. TP is at 1RR. 4. Vice versa for longs ## Specifications for CISD - CISD range consists of more than one consecutive bearish candles. - The high of the CISD range is the open of the first consecutive bearish candles. - CISD forms when the high of the CISD range gets closed above. - The CISD range can change if we keep making new lower lows. Always use the most recent cc candles from recent 5m swing high to new low. - Once an entry occurs, stop looking for another entry until a new 5m swing high or low is broken. ## Specifications for bearish FVG - A bearish fvg consists of three candles. Candle 1s low is the bearish fvg high. Candle 3s high is the bearish fvg low. Candle 2 is a displacement that creates a space between candle 1 low and candle 3 high. - The bearish FVG needs to be part of the cc candles that form the CISD range - only candle 2 needs to be in part of the cc candles that form the CISD range. - Save the first bearish fvg that appears inside the CISD range. - This can also change depending on new lower lows of cc down close candles ## Trade management - Hunt for only one setup until either a 5m swing high gets broken leading to a shirt or a new 5m swing low is broken leading to another long. ## Time specification - 9:30-11:00 is when you look for setups - hold trades past 11:00 if needed until tp or sl ## visuals - qualified CISD are drawn with a green line for longs, red line for shorts and orange line to notate the most recent CISD range high - stop loss in red, tp in green. - Put a small arrow with a bit of space between the candle. Green for longs under the entry candle and red for shores above the entry candle. - Reset everything after TP/SL or new trade except for the arrows indicating a trade was entered. This is a prompt i’ll give to claude. It already has model architecture and rules but it’s been having trouble giving me a consistent script. What do you think about this new prompt? is it clear
  
## Claude Response Summary  
-  ChatGPT gave me a number of things to clarify and the result is
```
Build a Pine Script strategy using the architecture and framework already established. Follow the rules below exactly.

# Long Setup (Vice Versa for Shorts)

1. A 5-minute swing low is broken.
    
2. After the swing low is broken, begin looking for a long setup on the 1-minute chart.
    
3. A long entry occurs immediately at market when:
    
    - A valid bullish CISD forms.
        
    - A valid bullish FVG exists within the active CISD range.
        
4. Stop loss is placed at the highest close of the bullish CISD range.
    
5. Take profit is placed at 1RR.
    
6. Reverse all logic for shorts.
    

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

A bearish FVG consists of three candles:

- Candle 1 low = FVG high.
    
- Candle 3 high = FVG low.
    
- Candle 2 is a displacement candle that creates a gap between Candle 1 low and Candle 3 high.
    

Rules:

- Only Candle 2 is required to belong to the active consecutive bearish candle sequence that forms the CISD range.
    
- Store only the first bearish FVG found within the active CISD range.
    
- If the CISD range extends with a new lower low, discard the previously stored FVG and rescan the updated CISD range.
    
- Store the earliest valid bearish FVG found in the updated range.
    

## Bullish FVG

A bullish FVG consists of three candles:

- Candle 1 high = FVG low.
    
- Candle 3 low = FVG high.
    
- Candle 2 is a displacement candle that creates a gap between Candle 1 high and Candle 3 low.
    

Rules:

- Only Candle 2 is required to belong to the active consecutive bullish candle sequence that forms the CISD range.
    
- Store only the first bullish FVG found within the active CISD range.
    
- If the CISD range extends with a new higher high, discard the previously stored FVG and rescan the updated CISD range.
    
- Store the earliest valid bullish FVG found in the updated range.
    

# Entry Requirements

A trade is entered immediately upon a CISD confirmation if a valid stored FVG exists within the active CISD range.

No retracement into the FVG is required.

The FVG is only a qualification filter for the setup.

For an entry to occur:

- The FVG must exist within the active CISD range.
    
- Candle 2 of the FVG must be part of the consecutive candles forming the active CISD range.
    
- If no valid FVG exists within the active CISD range, no trade is taken.
    

# Trade Management

- Only one setup may be active at a time.
    
- No additional setups may be evaluated until a fresh 5-minute swing high or swing low is broken.
    

# Time Rules

- Only search for new setups between 9:30 AM and 11:00 AM.
    
- New entries may only occur during this time window.
    
- Existing trades must remain active after 11:00 AM until TP or SL is reached.
    
- Do not force-close trades because the session window has ended.
    

# Visual Requirements

Draw qualified CISD levels:

- Green line for bullish CISD.
    
- Red line for bearish CISD.
    
- Orange line showing the active CISD range boundary used for confirmation.
    

Draw trade levels:

- Red line for stop loss.
    
- Green line for take profit.
    

Entry markers:

- Long entry: small green arrow below the entry candle with slight spacing.
    
- Short entry: small red arrow above the entry candle with slight spacing.
    

Reset all active drawings after TP, SL, or a new setup cycle begins.

Do not remove historical entry arrows. Entry arrows must remain on the chart permanently as trade history markers.
```
## What I Learned  
-  Technical language to use so things are more clear for Claude.
  
## Final Decision  
-  Created a new pine script and python backtester
  
## Related Files  
- [[v0.10 (CISD + IFVG)]]
- [[v1.4 (CISD + IFVG)]]