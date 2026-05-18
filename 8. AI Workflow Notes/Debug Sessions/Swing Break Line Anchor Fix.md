# AI Development Log - 
## Objective  
- Fix small aesthetic problems with the current version of the model.
  
## Important Prompt  
- Prompt 1
```
PLEASE KEEP EVERYTHING THE EXACT SAME EXCEPT WHAT I ASK YOU TO CHANGE.
  
When you detect a swing break you do it well. You draw out a dotted line size two with a colour associated to the low or high. This is good so far except you start drawing the break line from the candle that breaks the swing instead of the swing high itself.
  
I need you to draw the line from the swing high that was broken itself. CHANGE THIS
```
  - Prompt 2
```
to be clear i dont want it to be a bar earlier so it looks better, i want to anchor it exactly on the 5m swing high that was broken. Don't you store that candle somewhere so you know when to draw the break line once price trades to it
```
## Claude Response Summary  
-  With prompt 1 Claude proceeded to change the candle it was using to draw the break line by one candle. I continued to prompt it with prompt 2 and it said I was right, "but we never store the bar index of the swing candle itself. We need to add that."
  
## What I Learned  
-  How Claude is storing the levels. It keeps the price to know when to display the break but not the candle itself.
  
## Final Decision  
-  Updated version of the code except I'm keeping it as a pine script rather than a python file that outputs a pine script.
  
## Related Files  
-![[Pasted image 20260517231001.png]]
![[Pasted image 20260517231006.png]]
