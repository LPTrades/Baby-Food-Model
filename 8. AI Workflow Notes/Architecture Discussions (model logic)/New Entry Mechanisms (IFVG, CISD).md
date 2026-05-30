# AI Development Log - 
## Objective  
-  Introduce two new concepts that will be used as entry mechanism.
  
## Important Prompt  
>[!info] Prompt 1
  Tell me what a fvg is. Make an image.
  
>[!info] Prompt 2
  Now I want to introduce the IFVG. It's essentially the same thing as a fvg except it's formed on opposing side candles inside the break range. The IFVG forms when the current price closes through the gap completely and the idea is it should then be turned into support. If price is dropping and break a 5m swing, those bearish candles might have a bearish fvg that should act as resistance until it doesn't. Once price moves through it create a bullish fvg, it will inverse the bearish fvg and it should then also be treated as support and we call it an inverse fvg.

>[!info] Prompt 3
>Next is a Change In The State Of Delivery or CISD. 
 >
  This is also on the 1m chart. Same idea as IFVG but with consecutive candles. Lets say 5 down close candles form after one of the other. I need price to close above these candles. The close of the candle that is closed above the bodies (open of the first candle in the current delivery of consecutive candles) becomes the price level at which a CISD level is created.
  >
  >Same thing, lets make sure you understand then draw it.

>[!info] Prompt 4
>So what I would like to do with these two new concepts is implement them to an entry. You remember the concept 'break range'? As long as all three, the FVG, IFVG and a CISD form, I go long. It doesn't matter yet what order or what price I enter, only as soon as all three form.
>Above is a copy of my architecture. Please update the architecture to accommodate the new rules.
## Claude Response Summary  
>[!info] Prompt 1 Response
  A Fair Value Gap is a 3-candle pattern where a large displacement candle (candle 2) moves so aggressively that it leaves an unfilled gap between the wick of candle 1 and the wick of candle 3. That gap is a price range that was never traded through — the market skipped over it. Price tends to return to fill that gap![[Pasted image 20260522221420.png]]
  
  >[!info] Prompt 2
  >**Bearish FVG:**
  >- Acts as **resistance** while price is below it
  >- If price closes **above** the gap — it flips to **support** and becomes an IFVG
 > 
 > **Bullish FVG:**
 > - Acts as **support** while price is above it
 > - If price closes **below** the gap — it flips to **resistance** and becomes an IFVG
  No new candle formation needed. Just price closing through the gap is enough to flip it. Same concept as a support/resistance flip but with FVG zones instead of horizontal levels.![[Pasted image 20260522222701.png]]

>[!info] Prompt 3
>**CISD — Change In State Of Delivery:**
>
>1. You get a run of **consecutive same-direction candles** — say 5 bearish candles closing one after another (a "delivery" of price in one direction)
>2. The key level is the **open of the first candle** in that consecutive run — that's the top of the delivery block
>3. Price then needs to **close above** that open (for a bearish delivery) — meaning a candle closes above where the whole run started
>4. The moment that close happens, a **CISD level is created** at that open price
>5. That level now acts as **support** — same idea as the IFVG flip, just derived from consecutive candle bodies instead of a gap
>
**And the opposite:**
>
>- 5 consecutive bullish candles form a bullish delivery
>- Open of the first candle in the run is the bottom of the delivery
>- Price closes **below** that open
>- CISD level created at that open price — now acts as **resistance**
>
>**Key differences from IFVG:**
>
>- IFVG uses wick-to-wick gap space
>- CISD uses the open of the first candle in a consecutive run
>- No gap required — just consecutive bodies in one direction
>![[Pasted image 20260522224302.png]]

>[!info] Prompt 4
>[[Baby Food Model 3 2026.05.22]]
## Final Decision  
-  Will implement these step by step into the entry mechanism for the model to first create [[v0.7]] and then [[v1.1]]
