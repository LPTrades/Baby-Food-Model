# AI Development Log - 2026-05-19
## Objective  
-  Make sure Claude understands the anatomy of a FVG properly.
  
## Important Prompt  
-  Prompt 1
  ```
  generate a picture indicating what each level is in dashed and dotted lines
  ```
  ![[20250519 image for legend.png]]
- Prompt 2
  ```
  now show me what the high of the bullish fvg is and its low and the same with 
  bearish
  ```
- Prompt 3
  ```
  This is where im seeing the issue. You are confusing candle 1's high for the high of the fair value gap. The high of the bullish fvg is candle 3s low and the low of the fvg is candle 1s high. So tell me where the entry should be on a bullish fvg. a. Candle 1s high b. Candle 3s low c. something else
  And also draw a diagram side to side showing me a bullish and bearish example.
  ```


  
## Claude Response Summary  
-  Prompt 1
  ![[20260519 Legend.png]]
- Prompt 2
 ![[FVG HighLow detection mistake.png]]It was mistaking the high of the first candle as the high of the bullish fvg when it was actually the low. 
- Prompt 3
  ``` Claude answer
  Answer: b. Candle 3's low
  On a bullish FVG, price drops back down into the gap from above. So the entry is
  at the **top of the box** which is candle 3's low — that's where price re-enters
  the gap.This means the Pine Script needs to be corrected — currently it's using
  `high[2]` for the bullish entry when it should be using `low` (candle 3's low),
  and `low[2]` for the bearish entry when it should be `high` (candle 3's high).
  Want me to fix that now?
  ``` 
  ![[FVG HighLow detection fix.png]]
  

## What I Learned  
- If I asked Claude to code the entries, Claude would of entered long on the lower end of a bearish FVG. If I said "enter on the high of the FVG, it would of mistaken that for the high of candle 1.
  
## Final Decision  
-  I asked Claude to update Pinescript and give me [[v0.4]]. Here is a visual example:
