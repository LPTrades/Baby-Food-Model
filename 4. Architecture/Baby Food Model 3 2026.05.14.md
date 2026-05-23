
# **REVERSAL LIQUIDITY MODEL**  ICT-style 5m swing sweep with 1m FVG entry

---

## **Core Logic**

- 5m swing liquidity sweep (break of most recent swing high or low)
- First associated 1m FVG formed after the break
- Entry at top of bullish FVG or bottom of bearish FVG
- Quick 2R trades in the direction of the reversal

---

## **Stop Loss Logic**

- Place stop at the lowest low (longs) or highest high (shorts) that formed during the displacement leg — from the break candle to the FVG candle

---

## **Take Profit Logic**

- Minimum 2R from entry
- Extended to first 1m swing point beyond 2R if one exists

---

## **Session / Timing**

- Primary: 9:30 — 11:00 NY time
- Planned: 3:00 — 4:00 AM and 14:00-15:00
- Swings detected within session window only

---

## **Current Progress**

| Component                 | Status      |
| ------------------------- | ----------- |
| 5m swing detection        | Complete    |
| Break detection           | Complete    |
| FVG association           | Complete    |
| Entry visualization       | Complete    |
| SL logic                  | Complete    |
| TP logic (2R)             | Complete    |
| Trade close logic         | Complete    |
| Session timing            | Partial     |
| Pine Script visualization | Complete    |
| Python backtester         | Partial     |
| Live execution engine     | Not started |

---

## **Next Priorities**

1. Add configurable session windows to Pine Script
2. Validate model visually across 6 months of data
3. Build Python backtester matching Pine logic exactly
4. Collect trade data (entry, SL, TP, outcome, time, R)
5. Identify losing trade patterns and refine filters

---

## **What Success Looks Like**

- Model executes orders autonomously
- 6 months of live testing with positive returns
- Full historical backtesting capability
- Data-driven improvement loop — losing and winning trades logged and analyzed separately
- Clear rules for every scenario with no discretionary decisions required

---

## **Open Questions to Resolve**

- What hours are best to trade?
- Maximum allowed stop size in points before a setup is skipped?
- Should both long and short setups be active simultaneously or one at a time?
- What invalidates a setup mid-trade beyond SL being hit?
