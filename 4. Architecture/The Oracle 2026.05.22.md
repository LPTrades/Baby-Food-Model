# **REVERSAL LIQUIDITY MODEL** _ICT-style 5m swing sweep with 1m FVG entry_

---

### Core Logic

- 5m swing liquidity sweep (break of most recent swing high or low)
- Price must form all three of the following inside the break range on the 1m chart:
    - **FVG** — first fair value gap after the break
    - **IFVG** — a FVG that gets invalidated and flips role (resistance → support or support → resistance)
    - **CISD** — consecutive same-direction candles (2+) whose open of the first candle flips role when price closes through it
- Entry triggered as soon as all three are confirmed — order does not matter
- Direction of trade = direction of the reversal after the sweep

---

### Entry Logic

- Long: all three (FVG, IFVG, CISD) must form inside the break range after a swing low is swept
- Short: all three must form inside the break range after a swing high is swept
- Entry price TBD — currently triggers as soon as all three are confirmed

---

### Stop Loss Logic

- Place stop at the lowest low (longs) or highest high (shorts) that formed during the displacement leg — from the break candle to the FVG candle

---

### Take Profit Logic

- Minimum 2R from entry
- Extended to first 1m swing point beyond 2R if one exists

---

### Session / Timing

- Primary: 9:30 — 11:00 NY time
- Planned: 3:00 — 4:00 AM and 14:00 — 15:00
- Swings detected within session window only

---

### Current Progress

| Component                                     | Status      |
| --------------------------------------------- | ----------- |
| 5m swing detection                            | Complete    |
| Break detection                               | Complete    |
| FVG detection                                 | Complete    |
| IFVG detection                                | Not started |
| CISD detection                                | Not started |
| Triple confirmation entry (FVG + IFVG + CISD) | Not started |
| Entry visualization                           | Partial     |
| SL logic                                      | Complete    |
| TP logic (2R)                                 | Complete    |
| Trade close logic                             | Complete    |
| Session timing                                | Partial     |
| Pine Script visualization                     | Partial     |
| Python backtester                             | Partial     |
| Live execution engine                         | Not started |

---

### Next Priorities

1. Define and code IFVG detection on 1m
2. Define and code CISD detection on 1m
3. Build triple confirmation logic — all three must form inside break range
4. Determine exact entry price once all three are confirmed
5. Update Pine Script to visualize IFVG and CISD levels
6. Update backtester to match new entry logic
7. Add configurable session windows to Pine Script

---

### What Success Looks Like

- Model executes orders autonomously
- 6 months of live testing with positive returns
- Full historical backtesting capability
- Data-driven improvement loop — losing and winning trades logged and analyzed separately
- Clear rules for every scenario with no discretionary decisions required

---

### Open Questions to Resolve

- What is the exact entry price once all three confirm — market order, limit at IFVG, limit at CISD, or limit at FVG?
- Does the order of FVG → IFVG → CISD matter or is it purely all three present inside the break range?
- What is the maximum allowed stop size in points before a setup is skipped?
- What hours are best to trade?
- Should both long and short setups be active simultaneously or one at a time?
- What invalidates a setup mid-trade beyond SL being hit?

## Visuals
![[Pasted image 20260520184725.png]]
![[Pasted image 20260520184716.png]]
![[Pasted image 20260520184612.png]]