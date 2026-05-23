# AI Development Log - 2026-05-19
## Objective  
-  Get Claude to recognize what a break range is.
- Playing out [[Claude Break Range]] idea.
  
## Important Prompt  
-  Prompt 1
  ```
  Tell me what you see in this immage
  ```
  ![[Pasted image 20260519155240.png]]
- Prompt 2
  ```
  I want to change your definition "... from where the swing started to where it was broken." It is not to where it was broken, it goes past that to where it reverses and places a high. That is where I place my stop. Define the logic now.
  ```
- Prompt 3
  ```
  Implement the stop into the script. Draw a red shaded box from entry to stop. I
  only want to see one setup at a time. Draw a green shaded box aiming for 2RR. Do 
  not show outlines for the boxes
  ```
  
## Claude Response Summary  
-  Prompt 1
  ```
  What the break range represents:** The yellow box covers the entire range of the
  displacement move — from where the swing started to where it was broken. This is
  the area where you'd expect a fair value gap to form, and where you'd be looking
  for your entry.
  ```
- Prompt 2
  ```
  The logic is:
  - **Short:** stop = the new high price makes after breaking the swing high (top of
    the yellow box)
    - **Long:** stop = the new low price makes after breaking the swing low (bottom
      of the yellow box)
  ```
- Prompt 3
  [[v0.5]]
## Final Decision  
- The stop is showing now.