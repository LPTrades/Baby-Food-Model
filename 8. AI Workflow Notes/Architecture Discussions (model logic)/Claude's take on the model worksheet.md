# CISD + FVG Strategy — Full Architecture

_Source of truth for the NQ/MNQ 5m-break → 1m-CISD+FVG reversal model. Reflects the current Pine + Python logic._

---

## 0. One-line summary

On the 1m chart, after a 5m swing is taken out, the model looks for a **CISD level** (built from a consecutive same-direction candle run) and a **FVG** inside that move. When price closes back through the CISD level _and_ a valid FVG exists, it enters with a fixed-RR target and a stop at the run's extreme close.

---

## 1. Inputs

|Input|Default|Role|
|---|---|---|
|Entry session|09:30–11:00 ET|Window in which entries may trigger|
|Full session|09:30–12:00 ET|Window in which swings/breaks are valid|
|RR target|1|Reward-to-risk multiple for TP|
|5m data|—|Swing detection + break detection|
|1m data|—|CISD, FVG, entry, trade management|

Force-close: any open trade is flattened at **15:45** (Python only — Pine relies on `strategy.exit`).

---

## 2. The state machine

The model is always in exactly one of these phases:

```
        ┌─────────────────────────────────────────────┐
        │                                             │
        ▼                                             │
   ┌─────────┐   5m swing      ┌──────────┐   close   │
   │ WATCHING│   taken out     │  BIASED  │   thru     │
   │ bias=0  ├────────────────►│ bias=±1  ├── CISD ───►│
   │         │                 │          │  + FVG     │
   └─────────┘                 └──────────┘            │
        ▲                            │                 ▼
        │                            │           ┌──────────┐
        │      trade closes /        │           │ IN_TRADE │
        └──── session reset ─────────┴───────────┤ manage   │
                                                  │ TP/SL    │
                                                  └──────────┘
```

- **WATCHING** — swings are being captured on 5m; CISD is _pre-tracking_ on 1m.
- **BIASED** — a 5m break has set direction; CISD keeps tracking, FVG scans, entry armed.
- **IN_TRADE** — position open; only TP/SL/force-close logic runs.
- On exit → full reset → back to WATCHING.

---

## 3. Complete state inventory

### Swing state

- `recent_sh`, `recent_sl` — most recent unbroken 5m swing high/low level
- `recent_sh_time`, `recent_sl_time` — bar time of that swing (for drawing)

### Direction

- `bias` — `0` none, `1` long, `-1` short
- `setup_used` — true once a trade fires; blocks re-entry until reset

### Bullish CISD (for longs) — consecutive **bearish** run

- `bear_run_start` / `bear_run_count` — run anchor + length
- `bear_run_open` — open of the **first** bearish candle (becomes the level)
- `bear_run_sl` — lowest close in the run (becomes stop)
- `cisd_long_start` / `cisd_long_end` — captured range bounds
- `cisd_long_high` — the CISD level (= `bear_run_open`, locked at run start)
- `cisd_long_low` — extends with each new lower low
- `cisd_long_sl` — stop level

### Bearish CISD (for shorts) — consecutive **bullish** run

- Mirror of the above (`bull_run_*`, `cisd_short_*`), with `cisd_short_low` as the level and `cisd_short_high` extending up.

### FVG (directional)

- `fvg_long_high` / `fvg_long_low` / `fvg_long_valid`
- `fvg_short_high` / `fvg_short_low` / `fvg_short_valid`

### Trade

- `entry_price`, `sl_price`, `tp_price`, `in_trade`

---

## 4. Subsystem: 5m swing detection

Three-candle fractal on closed 5m bars (a = oldest, b = middle, c = newest):

- **Swing low** when `b.low < a.low` AND `b.low < c.low` → level = `b.low`
- **Swing high** when `b.high > a.high` AND `b.high > c.high` → level = `b.high`
- Confirmed on the **close of candle c**.

Only the **most recent** swing of each type is held. A newer swing low overwrites the old `recent_sl`.

---

## 5. Subsystem: 5m break detection → bias

While `not in_trade and not setup_used`:

- `low < recent_sl` → **bias = LONG**, clear `recent_sl`
- `high > recent_sh` → **bias = SHORT**, clear `recent_sh`

The break is the trigger that turns "watching" into "armed."

---

## 6. Subsystem: CISD tracking ← _the contentious core_

**Gate (current):** runs while `in_entry_session AND (swing exists OR bias is set) AND not in_trade AND not setup_used`.

For **bullish CISD** (longs), each 1m bar:

1. **Bearish candle, new sequence** (prev candle not bearish):
    - Start a fresh run; `bear_run_open = open`, `bear_run_sl = close`, count = 1.
    - **Invalidate the old stored CISD range and FVG.**
2. **Bearish candle, continuation** (prev candle also bearish):
    - `count += 1`; `bear_run_sl = min(sl, close)`.
3. **Once `count >= 2`:**
    - Capture range: `cisd_long_high = bear_run_open` (locked), `cisd_long_low = low`, `cisd_long_sl = bear_run_sl`.
    - **Reset FVG** (`fvg_long_valid = false`) so it re-scans against the updated range.
4. **Non-bearish candle:** reset the run tracker only; keep the stored CISD range.

Bearish CISD (shorts) is the exact mirror with bullish runs.

**Rules being enforced:**

- CISD level = open of the **first** candle in the active consecutive run.
- Active run = the **most recent** valid consecutive sequence.
- A new sequence wipes the old level.
- Stop = extreme close of the run.

---

## 7. Subsystem: FVG scanning

Scans for the first valid 3-candle gap from `cisd_start` onward (no upper-bound window):

- **Long (bearish FVG):** `c1.low > c3.high` → `fvg_high = c1.low`, `fvg_low = c3.high`
- **Short (bullish FVG):** `c3.low > c1.high` → `fvg_high = c3.low`, `fvg_low = c1.high`

Stores the **first** one found and sets `fvg_*_valid = true`. Re-scans whenever the CISD range changes (because the change resets `fvg_*_valid`).

---

## 8. Subsystem: entry logic

- **Long:** `bias==1 AND cisd_long_high exists AND close > cisd_long_high AND fvg_long_valid AND in_entry_session`
- **Short:** `bias==-1 AND cisd_short_low exists AND close < cisd_short_low AND fvg_short_valid AND in_entry_session`

On fire: `entry = close`, `sl = cisd_*_sl`, `tp = entry ± risk × RR`, set `in_trade`, `setup_used`, reset `bias = 0`.

---

## 9. Subsystem: trade management

- Long: TP if `high >= tp`, SL if `low <= sl`. Short mirrors.
- Tie-break (both hit same bar): decided by which side the **open** is closer to.
- Force-close at 15:45 at the bar open (Python).
- On any exit → full reset → WATCHING.

---

## 10. Resets

|Trigger|What resets|
|---|---|
|New session|Everything: swings, bias, runs, CISD, FVG|
|New consecutive run starts|That direction's stored CISD range + FVG|
|Non-bearish/bullish candle|The run tracker only (keeps stored range)|
|Trade close / force-close|All CISD/FVG/run/trade state; `setup_used` cleared|

---

## 11. ⚠️ The structural conflict causing the whack-a-mole

Every fix in this thread has been fighting **one unresolved question**:

> **Which consecutive run is the CISD, and until what moment is it allowed to change?**

Two requirements have been pulling against each other:

- **"Use the most recent run, keep re-anchoring"** → matches your Chart A→B example where the level moves _down_ after the break.
- **"Don't lose entries"** → the model entered cleanly when the CISD was captured once and held.

These collide because of **one line**: every time the CISD range updates, we do `fvg_*_valid = false`.

### The actual entry-killer

When the CISD keeps re-anchoring after the break (current behavior), the FVG is reset on **every** re-anchor. So `fvg_valid` rarely survives long enough to be `true` _on the same bar_ that price closes through the CISD level. That's why "so many valid entries" disappeared — not because the level is wrong, but because the FVG flag keeps getting wiped right before confirmation.

So the real design knobs are **two separate decisions**, not one:

1. **CISD re-anchoring window** — until when may the level move?
    - (a) Freeze at break, or
    - (b) Keep updating until entry (current), or
    - (c) Keep updating but only to _lower_ lows (longs) / higher highs (shorts).
2. **FVG persistence** — once a valid FVG is found, does a CISD re-anchor _invalidate_ it, or does it **persist** as long as its candles still sit within the (possibly extended) range?

Almost certainly you want **FVG to persist** (decision 2 = persist), which decouples it from the re-anchoring and brings the entries back without reverting the level behavior you asked for.

---

## 12. Decision matrix to lock down

Fill these in once and the model stops oscillating:

| #   | Question                                                         | Options                                 | Your call         |
| --- | ---------------------------------------------------------------- | --------------------------------------- | ----------------- |
| 1   | CISD eligible to update after break?                             | freeze / until-entry / only-new-extreme | 3                 |
| 2   | Does a CISD re-anchor invalidate a found FVG?                    | yes / **persist**                       | 1                 |
| 3   | If FVG persists, must its candles stay inside the current range? | yes / no                                | 2                 |
| 4   | One setup per swing break, or re-arm if invalidated?             | one / re-arm                            | 1 entry per break |
| 5   | CISD level = first-candle open always?                           | yes / other                             | 1                 |

Once 1–3 are set, the entry count is fully determined and Pine + Python will agree.