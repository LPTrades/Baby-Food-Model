# AI Development Log - 2026/05/28

## Objective

* Implement a CISD + IFVG python and pine script version of the model according to [[The Oracle 2026.05.22]]

## Important Prompt

- "do you remember what a CISD is? Draw it for me"
- "The CISD is not drawing even though I can see consecutive bear candles. The script is loaded, swing lines are drawing, and the bear candles are there"
- "When a 5m swing low is broken, I want you to go back and save all the 1m candles from the recent 5m swing high to the new low. The most recent consecutive run of down close candles inside that range must be saved... Inside that consecutive run I need you to draw an orange line at the highest open (the first down close candle in the series of down close candles leading to the lowest low)"

## Claude Response Summary

* Prompt 1: Claude drew a nice diagram of the CISD I had taught it from earlier discussions in [[New Entry Mechanisms (IFVG, CISD)]]
  ![[Pasted image 20260529153112.png]]
* Prompt 2: I isolated the problem for Claude with an example with my own annotations (image below) so it knows exactly what I'm talking about. Claude went through the model step by step applying it to the image. I came to find out that it was only counting bear candles BENEATH the 5m break line once a 1m candle closes beneath the level instead of the whole run.
  ![[Pasted image 20260529153259.png]]
* Prompt 3: This seemed to fix it. Claude understood exactly what I meant. I wanted it to track the entire run involved in breaking the 5m swing low. It's in this range, from the moment a 5m swing is created, that it started scanning for FVG and consecutive candles even before breaking an opposing 5m swing.

## Final Decision

* Versions finalized for both [[v0.9 (CISD + IFVG)]] and [[v1.3 (CISD + IFVG)]].

## Related Files

* cisd_ifvg_model.pine → [[v0.9 (CISD + IFVG)]]
* cisd_ifvg_backtest.py → [[v1.3 (CISD + IFVG)]]