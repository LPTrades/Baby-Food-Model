# AI Development Log — 2026-05-23

## Objective

Extend the v0.6 Pine Script ("Swing - First FVG Only") to detect an **Inverse Fair Value Gap (IFVG)** in addition to the existing FVG, off the same 5m swing sweep / break. Detection and visualization only — no entry, stop loss, take profit, or trade management.

- **FVG (existing, v0.6):** first continuation gap after the break.
- **IFVG (new):** an opposite-side gap that price trades back into and closes through, flipping its role.
    - Long: a **bearish** gap that price closes **above** → flips to a **bullish IFVG**.
    - Short: a **bullish** gap that price closes **below** → flips to a **bearish IFVG**.
- Final requirement: run FVG and IFVG as **two independent detectors in parallel** off the same break, each with its own state and its own box.

---

## Important Prompt

> "If you take a look at the pine script v0.6, do you see how we make the first 1m FVG show up after a break? I want you to recreate that except use a IFVG instead of a FVG. So for a long setup, instead of using bullish candles to form a bullish fvg, youre using bearish candles forming a bearish fvg that price trades back into and then closes above turning them into a bullish IFVG."

Two clarifications that shaped the final logic:

> "I should of clarified, its the last bearish fvg you want to keep and the first one to be inversed."

> "i want them to run as different gaps running in parallel off the same break"

---

## Claude Response Summary

Development happened in three stages:

1. **IFVG-only build.** Replaced the v0.6 FVG section with a two-step IFVG detector: (1) find an opposite-side gap and remember the edge price must close through; (2) when a later bar closes through that edge, draw the flipped IFVG box. Entry/SL/TP machinery was stripped out per instruction. The box was anchored to the _original gap's_ location/levels so it marks the actual level price closed back through, revealed at the moment of confirmation.
2. **Switch from first gap to last gap.** Per the clarification, the IFVG detector was changed to track the **most recent** opposite-side gap (overwriting as newer ones form) rather than locking on the first. The flip check was reordered to run **before** the tracking update each bar, so a gap cannot both form and flip on the same bar — inversion requires a pre-existing gap.
3. **Add FVG back, in parallel.** Re-added the v0.6 first-continuation-FVG detector alongside the IFVG detector. The two share only `mode` and the break that resets them. State was renamed to avoid collision — the IFVG flag became `ifvgFound`, leaving `fvgFound` for the FVG detector. Each detector has its own box, and both clear on the next sweep. Boxes were styled differently (FVG solid border / lighter fill; IFVG dashed border / heavier fill) to tell them apart on the chart.

Final file: [[v0.7]]

---

## What Claude Learned

- **"First" vs "last" gap is a meaningful design choice.** For an IFVG, the last opposite gap before the reversal is the one closest to price and therefore the first to get inverted on the way back — so tracking the latest gap (not the first) matches the actual price mechanic.
- **Bar-evaluation order matters in Pine.** Because detection and flip logic run on the same bar, the flip check has to evaluate against the gap as it stood _before_ that bar's update. Reordering (check flip → then update tracked gap) prevents a same-bar form-and-flip, which would be logically impossible.
- **Independent detectors need independent state.** Reusing `fvgFound` for both detectors would have caused them to block each other. Separating into `fvgFound` / `ifvgFound` (plus dedicated boxes) let both run truly in parallel.
- **FVG and IFVG look for opposite gap polarities**, so they rarely sit on the same candles and should remain visually distinct on the chart.

---

## Final Dec

v0.7 delivers two parallel, independent gap detectors off a single 5m swing break:

- **FVG** — first continuation gap (v0.6 behavior preserved), solid-border box.
- **IFVG** — last opposite-side gap that price closes through and inverts, dashed-border box.

Both are visualization-only and reset on each new sweep. Entry price, stop loss, take profit, and trade management are intentionally **not** implemented yet and remain open items (entry price in particular is still an open question in the Oracle model doc). Next candidate steps, when ready: define IFVG-based entry, mid-trade invalidation (e.g. price closing back through the IFVG against the trade), and reintroduce SL/TP logic.
  
## Related Files  
-