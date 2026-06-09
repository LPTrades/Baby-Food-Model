# AI Development Log - 2026-06-08
## Objective  
-  Fix bugs in faulty trades
  
## Important Prompt  
-  
	Here is two .csv files with relevant data for the days I want to debug certain trades. Also I pasted the python script for the model. Overall the model works well and prints mostly good trades but here are three that were wrong.
	
	Trade 1: 2/10/2026 10:34 SHORT W 25420.75 2/10/2026 10:31 25406.5 25381.5 25431.5 1 44.05 The script goes short at the close of 10:34. It thinks the CISD level is at 25420.75. However, the CISD level is wrong and shout be at the open of the 10:30 candle instead of the 10:31 candle since that candle is also bullish. The script here enters too early.
	
	Trade 2: 2/16/2026 11:27 SHORT W 24740 2/16/2026 11:26 24724 24696.5 24751.5 1 27.36 The script goes short at 11:27 on the close of an up close candle. Shorts should be armed but the there is no fvg formed by the consecutive bullish candles creating the CISD range (11:14 and 11:15). A +fvg forms at the candle of entry with the middle candle being 11:26 but this is not part of the CISD range.
	
	Trade 3: 2/24/2026 11:20 LONG W 24983.25 2/24/2026 11:16 24997.75 25019 24976.5 1 40.74 The script went long at 11:20 on the close of a down close candle. Longs should be unarmed since a 5m short term high was broken, we should looking for shorts. The CISD for the long the script tracks are the 10:58 and 10:59 down close candles. However no -fvg forms inside that range so no trade. As price closes above the CISD it makes a new 5m short term high at 11:05.
	
	I can provide visual images of the trades too. Tell me what you think happened
  
## Claude Response Summary  
- Bug 1: Script walks backwards to find the CISD instead of storing candles based on a state. This bug caused open trades to skip any relevant CISD candles for another trade immediately after.
- Bug 2: The FVG search window ran past the CISD range. Trades were entered far after the CISD formed on pullbacks that would form FVGs.
- Bug 3: CISDs are only invalidates on new sessions, a new extreme on the same side is made or a trade is closed. It does not invalidate and look for a new CISD if the opposite side makes a new 5m break.
  
## Final Decision  
-  Implemented [[v1.7]]