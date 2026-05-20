# AI Development Log - 
## Objective  
-  Make the stop loss, take profit and FVG stay on the chart until the next entry.
  
## Important Prompt  
-  Prompt 1
  ```
  as soon as a new break line shows up, the sl and tp go away. I dont want this
  because id be holding the trade until another entry shows up where i reverse the
  position
  ```
- Prompt 2
  ```
  get rid of the tp and sl when price reaches take profit or stop
  loss
  ```
  
## Claude Response Summary  
-  Prompt 1
  ```
  you want the SL and TP to stay until a **new entry arrow** appears, not when a
  new break line appears. So only clear them when `entryHit` becomes true again on
  a new setup.
  ```
- Prompt 2
  Added a new variable to track if a trade is open in and a new state called 'tradeMode' that separates the entry and close logic from the break line logic and preserved 'entryHit'. I asked it to do the same for the FVG.
## What I Learned  
-  The different states the script is in to track what stays and goes on the chart.
  
## Final Decision  
-  Update [[v0.5]] to [[v0.6]].
  
## Related Files  
- [[FVG, SL and TP visibility - CLOSED]]