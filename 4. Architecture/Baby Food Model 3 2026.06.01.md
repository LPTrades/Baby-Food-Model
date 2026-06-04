# **REVERSAL LIQUIDITY MODEL** _ICT-style 5m swing sweep with 1m FVG entry_

---

### Core Logic

- 5m swing liquidity sweep (break of most recent swing high or low)
- Price must form both of the following inside the break range on the 1m chart:
    - **IFVG** — a FVG that gets invalidated and flips role (resistance → support or support → resistance)
    - **CISD** — consecutive same-direction candles (2+) whose open of the first candle flips role when price closes through it
- Entry triggered as soon as both are confirmed
- Direction of trade = direction of the reversal after the sweep

---

### Swing Logic
#### A 5m swing low consists of:
- three 5m candles making a low, lower low, and higher low
- All of these candles are consecutive
- The swing low level is the second candle's low, the lower low
#### A 5m swing high consists of:
- three 5m candles making a high, higher high, and lower high
- All of these candles are consecutive
- The swing high level is the second candle's high, the higher high
#### The bearish break happens:
- Immediately when price trades beneath the recent 5m swing low
- Do not wait until the current 5m candle closes
#### The bullish break happens:
- Immediately when price trades above the recent 5m swing high
- Do not wait until the current 5m candle closes

---

### CISD Specifications

#### Bullish CISD (for longs)

- The CISD range consists of more than one consecutive bearish candle.
- The high of the CISD range is the open of the first bearish candle in the consecutive bearish sequence.
- A bullish CISD forms when price closes above the high of the CISD range.
- The stop loss is placed at the lowest closing price among all candles in the active CISD range.
- The active CISD range is always the most recent sequence of consecutive bearish candles.
- If a new lower low is made by consecutive bearish candles, the CISD range must update to include the new candles.

#### Bearish CISD (for shorts)

- The CISD range consists of more than one consecutive bullish candle.
- The low of the CISD range is the open of the first bullish candle in the consecutive bullish sequence.
- A bearish CISD forms when price closes below the low of the CISD range.
- The stop loss is placed at the highest closing price among all candles in the active CISD range.
- The active CISD range is always the most recent sequence of consecutive bullish candles.
- If a new higher high is made by consecutive bullish candles, the CISD range must update to include the new candles.

---

### Entry Logic

- Long: both (IFVG, CISD) must form inside the break range after a swing low is swept
- Short: both must form inside the break range after a swing high is swept
- Entry price TBD — currently triggers as soon as two are confirmed

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

| Component                               | Status      |
| --------------------------------------- | ----------- |
| 5m swing detection                      | Not started |
| Break detection                         | Not started |
| IFVG detection                          | Not started |
| CISD detection                          | Not started |
| Double confirmation entry (IFVG + CISD) | Not started |
| Entry visualization                     | Complete    |
| SL logic                                | Complete    |
| TP logic (1R)                           | Complete    |
| Trade close logic                       | Complete    |
| Session timing                          | Partial     |
| Pine Script visualization               | Complete    |
| Python backtester                       | Partial     |
| Live execution engine                   | Not started |

---

### Next Priorities

1. Define and code IFVG detection on 1m
2. Define and code CISD detection on 1m
3. Build double confirmation logic — all three must form inside break range
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

- What is the exact entry price once both confirm — market order, limit at IFVG or limit at CISD?
- What is the maximum allowed stop size in points before a setup is skipped?
- What hours are best to trade?
- Should both long and short setups be active simultaneously or one at a time?
- What invalidates a setup mid-trade beyond SL being hit?

## Visuals
![[Pasted image 20260520184725.png]]
![[Pasted image 20260520184716.png]]
![[Pasted image 20260520184612.png]]