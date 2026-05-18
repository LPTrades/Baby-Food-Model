# AI Development Log - 
## Objective  
- Make sure the break line is drawn from the right candle index on the 1m.
  
## Important Prompt  
-  Everything works well on the 5m chart, except when dropping down to the 1m chart, things get messy again. I think you store the candle index properly for the 5m chart but you don't convert that index so the 1m chart draws it from the same 5m candle. CHANGE THIS
  
## Claude Response Summary  
-  "You're exactly right. The `bar_index` is stored in 1m bars when the script runs on the 1m chart, but the swing detection comes from 5m data via `request.security`. The indexes don't match. The fix is to store the **time** of the swing candle instead of the bar index, then use `xloc.bar_time` to anchor the line."
  
## What I Learned  
-  
  
## Final Decision  
-  Updated script to [[v0.3]]
  
## Related Files  
-This was what I was seeing on the 1m chart: with [[v0.2]]![[Pasted image 20260518102905.png]]
Meanwhile the 5m chart:![[Pasted image 20260518103000.png]]
Now with [[v0.3]] 5m and 1m below:
![[Pasted image 20260518104824.png]]
![[Pasted image 20260518104849.png]]