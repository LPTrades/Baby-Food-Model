# AI Development Log - 2026-06-09
## Objective  
-  Measure the distribution of RR over different win rates and take profit styles with v1.8
  
## Important Prompt  
-  Prompt 1: I gave chatGPT my expectancy per rr below for a handful of different RR targets.
| rr |  exp |
|0.5|**0.027**|
|0.6|0.018|
|0.7|0.011|
|0.8|0.014|
|0.9|0.020|
|1.0|0.015|
|1.5|0.012|
|2.0|0.016|
|2.5|0.007|
|3.0|0.009|
  - Prompt 2: Uploaded the results for reversal only TP
## Claude Response Summary  
-  Prompt 1: Chat suggested that my expectancy curve is not monotonic but differences between 0.5 and 0.9 (which seem to be the best performing) are not so huge to conclude 0.5rr is the most optimal. It also pointed out my win rate doesn't break down over larger RR targets but the expectancy decreases. It asked why and I told it because in profit trades get reversed when an opposing trades shows instead of going to stop loss but not going to profit all the way, hence the small rr. This lead chat to ask me to test reversal only TP (no set take profit), Also as i'm writing this i am asking myself: if larger RR has a good win rate but still low expectancy, what if that's because too many trades are taken with the CISD level or entry being too far from the stop?
- Prompt 2: This does not work at all and chat asked me to refocus on rr between 0.4 and 1. I should pick the one that wins most consistently year by year.
  
## What I Learned  
- My model is not monotonic.
- Larger RR might only keep expectancy low because stops might be too big.
  
## Final Decision  
-  Measure RR distribution from 0.4 to 1rr.