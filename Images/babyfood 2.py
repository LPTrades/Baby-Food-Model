"""
CISD + FVG Backtest  — NQ 1m + 5m
Decision matrix locked:
1. CISD updates only on new extreme (lower low for longs, higher high for shorts)
2. FVG invalidates only when CISD range makes a new extreme
3. FVG candles do not need to stay inside current range
4. One entry per swing break
5. CISD level = open of first candle in capturing sequence

OPPOSING-SIGNAL MODE (new toggle):
  ignore  = original behavior; opposite 5m break while in a trade is invisible.
  exit    = an opposite 5m break closes the open trade at market, then resumes flat.
  reverse = an opposite 5m break closes the open trade AND arms the opposite bias,
            so the engine immediately hunts the opposite CISD+FVG entry.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os, sys, random
from datetime import time as dtime
from collections import defaultdict

# ─────────────────────────────────────────────
# INPUTS
# ─────────────────────────────────────────────
def prompt(label, default):
    val = input(f"{label} [{default}]: ").strip()
    return val if val else str(default)

print("=" * 55)
print("   CISD + FVG Backtester")
print("=" * 55)

data_dir   = r"C:\tradingProject\Data"
file_5m    = prompt("5m data filename",          "5m.csv")
file_1m    = prompt("1m data filename",          "1m.csv")
years_raw  = prompt("Years (comma-separated)",   "2021,2022,2023,2024,2025,2026")
sess_start = prompt("Session start (HH:MM)",     "09:30")
sess_end   = prompt("Session end   (HH:MM)",     "12:00")
rr_input   = float(prompt("RR target",           "1"))

opp_raw  = prompt("Opposing-signal mode (ignore/exit/reverse)", "ignore").strip().lower()
opp_mode = opp_raw if opp_raw in ("ignore", "exit", "reverse") else "ignore"

years_to_test = [int(y.strip()) for y in years_raw.split(",")]
path_5m       = os.path.join(data_dir, file_5m)
path_1m       = os.path.join(data_dir, file_1m)
sess_start_t  = dtime(*map(int, sess_start.split(":")))
sess_end_t    = dtime(*map(int, sess_end.split(":")))

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
def load_ohlc(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if "time" in cl or "date" in cl: col_map[c] = "datetime"
        elif cl in ("o","open"):          col_map[c] = "open"
        elif cl in ("h","high"):          col_map[c] = "high"
        elif cl in ("l","low"):           col_map[c] = "low"
        elif cl in ("c","close"):         col_map[c] = "close"
    df.rename(columns=col_map, inplace=True)
    if "datetime" not in df.columns:
        df.rename(columns={df.columns[0]: "datetime"}, inplace=True)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.sort_values("datetime", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

print("\nLoading data...")
df5 = load_ohlc(path_5m)
df1 = load_ohlc(path_1m)
print(f"  5m: {len(df5):,}  {df5['datetime'].iloc[0]} → {df5['datetime'].iloc[-1]}")
print(f"  1m: {len(df1):,}  {df1['datetime'].iloc[0]} → {df1['datetime'].iloc[-1]}")

df5 = df5[df5["datetime"].dt.year.isin(years_to_test)].reset_index(drop=True)
df1 = df1[df1["datetime"].dt.year.isin(years_to_test)].reset_index(drop=True)
print(f"  After filter → 5m: {len(df5):,}  1m: {len(df1):,}")
print(f"  Opposing-signal mode: {opp_mode}")

# ─────────────────────────────────────────────
# CANDLE HELPERS
# ─────────────────────────────────────────────
def is_bearish(bar): return bar["close"] < bar["open"]
def is_bullish(bar): return bar["close"] > bar["open"]

# ─────────────────────────────────────────────
# 5M SWING DETECTION
# ─────────────────────────────────────────────
def build_5m_swings(df):
    events = []
    for i in range(2, len(df)):
        a, b, c = df.iloc[i-2], df.iloc[i-1], df.iloc[i]
        if b["low"]  < a["low"]  and b["low"]  < c["low"]:
            events.append({"type":"swing_low",  "level":b["low"],
                           "confirmed_time": c["datetime"]})
        if b["high"] > a["high"] and b["high"] > c["high"]:
            events.append({"type":"swing_high", "level":b["high"],
                           "confirmed_time": c["datetime"]})
    return sorted(events, key=lambda e: e["confirmed_time"])

swing_events = build_5m_swings(df5)
print(f"  5m swing events: {len(swing_events):,}")

# ─────────────────────────────────────────────
# SESSION HELPERS
# ─────────────────────────────────────────────
def in_entry_session(dt):
    return sess_start_t <= dt.time() <= sess_end_t

force_close_time = dtime(15, 45)

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
BIAS_NONE  =  0
BIAS_LONG  =  1
BIAS_SHORT = -1

trades       = []
bias         = BIAS_NONE
setup_used   = False
in_trade     = False
active_trade = None

recent_sw_low  = None
recent_sw_high = None

# Bullish CISD
bear_run_start  = None
bear_run_count  = 0
bear_run_open   = None
bear_run_sl     = None
bear_run_low    = None

cisd_long_start = None
cisd_long_end   = None
cisd_long_high  = None
cisd_long_low   = None
cisd_long_sl    = None
cisd_long_fvg_e = None

fvg_long_valid  = False
fvg_long_stored = None

# Bearish CISD
bull_run_start  = None
bull_run_count  = 0
bull_run_open   = None
bull_run_sl     = None
bull_run_high   = None

cisd_short_start = None
cisd_short_end   = None
cisd_short_high  = None
cisd_short_low   = None
cisd_short_sl    = None
cisd_short_fvg_e = None

fvg_short_valid  = False
fvg_short_stored = None

sq_ptr = 0

# ─────────────────────────────────────────────
# RESET HELPERS
# ─────────────────────────────────────────────
def reset_bear_run():
    global bear_run_start, bear_run_count, bear_run_open, bear_run_sl, bear_run_low
    bear_run_start = None; bear_run_count = 0
    bear_run_open  = None; bear_run_sl    = None; bear_run_low = None

def reset_bull_run():
    global bull_run_start, bull_run_count, bull_run_open, bull_run_sl, bull_run_high
    bull_run_start = None; bull_run_count = 0
    bull_run_open  = None; bull_run_sl    = None; bull_run_high = None

def reset_long_cisd():
    global cisd_long_start, cisd_long_end, cisd_long_high, cisd_long_low, cisd_long_sl, cisd_long_fvg_e
    global fvg_long_valid, fvg_long_stored
    cisd_long_start = cisd_long_end = cisd_long_high = cisd_long_low = cisd_long_sl = cisd_long_fvg_e = None
    fvg_long_valid  = False
    fvg_long_stored = None

def reset_short_cisd():
    global cisd_short_start, cisd_short_end, cisd_short_high, cisd_short_low, cisd_short_sl, cisd_short_fvg_e
    global fvg_short_valid, fvg_short_stored
    cisd_short_start = cisd_short_end = cisd_short_low = cisd_short_high = cisd_short_sl = cisd_short_fvg_e = None
    fvg_short_valid  = False
    fvg_short_stored = None

def reset_long_fvg():
    global fvg_long_valid, fvg_long_stored
    fvg_long_valid  = False
    fvg_long_stored = None

def reset_short_fvg():
    global fvg_short_valid, fvg_short_stored
    fvg_short_valid  = False
    fvg_short_stored = None

def reset_all():
    global bias, setup_used
    bias       = BIAS_NONE
    setup_used = False
    reset_bear_run()
    reset_long_cisd()
    reset_bull_run()
    reset_short_cisd()

# ─────────────────────────────────────────────
# FVG SCAN — no upper bound, c2 >= cisd_start
# ─────────────────────────────────────────────
def scan_fvg_long(cisd_start, cisd_end, i1):
    # FVG must sit inside the CISD displacement run (middle candle in
    # [cisd_start, cisd_end]); +1 allows the immediate breaker candle.
    # Never look past the current bar i1.
    n  = len(df1)
    hi = min(cisd_end + 2, i1)
    for c2_idx in range(cisd_start, hi):
        c1_idx = c2_idx - 1
        c3_idx = c2_idx + 1
        if c1_idx < 0 or c3_idx >= n:
            continue
        c1 = df1.iloc[c1_idx]
        c3 = df1.iloc[c3_idx]
        if c1["low"] > c3["high"]:
            return {
                "fvg_high":     c1["low"],
                "fvg_low":      c3["high"],
                "candle2_time": df1.iloc[c2_idx]["datetime"],
            }
    return None

def scan_fvg_short(cisd_start, cisd_end, i1):
    n  = len(df1)
    hi = min(cisd_end + 2, i1)
    for c2_idx in range(cisd_start, hi):
        c1_idx = c2_idx - 1
        c3_idx = c2_idx + 1
        if c1_idx < 0 or c3_idx >= n:
            continue
        c1 = df1.iloc[c1_idx]
        c3 = df1.iloc[c3_idx]
        if c3["low"] > c1["high"]:
            return {
                "fvg_high":     c3["low"],
                "fvg_low":      c1["high"],
                "candle2_time": df1.iloc[c2_idx]["datetime"],
            }
    return None

# ─────────────────────────────────────────────
# MAIN BACKTEST LOOP
# ─────────────────────────────────────────────
n1 = len(df1)
print("\nRunning backtest...")

for i1 in range(n1):
    bar    = df1.iloc[i1]
    bar_dt = bar["datetime"]
    bar_t  = bar_dt.time()

    # ── Advance swing queue ───────────────────
    while sq_ptr < len(swing_events):
        ev = swing_events[sq_ptr]
        if ev["confirmed_time"] <= bar_dt:
            if ev["type"] == "swing_low":
                recent_sw_low = {"level": ev["level"]}
                reset_bear_run()   # reset run only, keep stored CISD
            else:
                recent_sw_high = {"level": ev["level"]}
                reset_bull_run()   # reset run only, keep stored CISD
            sq_ptr += 1
        else:
            break

    # ── New session reset ─────────────────────
    is_new_session = (
        bar_t == sess_start_t or
        (i1 > 0 and df1.iloc[i1-1]["datetime"].date() != bar_dt.date()
         and in_entry_session(bar_dt))
    )
    if is_new_session and not in_trade:
        recent_sw_low  = None
        recent_sw_high = None
        reset_all()

    # ── Force-close 15:45 ────────────────────
    if in_trade and bar_t >= force_close_time:
        d  = active_trade["direction"]
        ep = bar["open"]
        r  = (ep - active_trade["entry"]) / active_trade["risk"] if d == "long" \
             else (active_trade["entry"] - ep) / active_trade["risk"]
        active_trade.update(exit_price=ep, exit_time=bar_dt,
                            result="eod", r=r, win=(r > 0))
        trades.append(active_trade)
        active_trade = None
        in_trade     = False
        setup_used   = False
        reset_all()
        continue

    # ── Manage open trade ─────────────────────
    if in_trade:
        d  = active_trade["direction"]
        tp = active_trade["tp"]
        sl = active_trade["sl"]
        hit_tp = (d=="long"  and bar["high"] >= tp) or (d=="short" and bar["low"]  <= tp)
        hit_sl = (d=="long"  and bar["low"]  <= sl) or (d=="short" and bar["high"] >= sl)
        if hit_tp or hit_sl:
            if hit_tp and hit_sl:
                hit_sl = (d=="long"  and bar["open"] <= sl) or \
                         (d=="short" and bar["open"] >= sl)
                hit_tp = not hit_sl
            r = rr_input if hit_tp else -1.0
            active_trade.update(
                exit_price = tp if hit_tp else sl,
                exit_time  = bar_dt,
                result     = "tp" if hit_tp else "sl",
                r          = r, win=hit_tp,
            )
            trades.append(active_trade)
            active_trade = None
            in_trade     = False
            setup_used   = False
            reset_all()
            continue

        # ── Opposing-signal handling (ignore = original behavior) ──
        # Opposite 5m break vs the open trade:
        #   long  → a swing HIGH is swept (bar high > recent swing high)
        #   short → a swing LOW  is swept (bar low  < recent swing low)
        if opp_mode != "ignore":
            opp_break = (
                (d == "long"  and recent_sw_high is not None and bar["high"] > recent_sw_high["level"]) or
                (d == "short" and recent_sw_low  is not None and bar["low"]  < recent_sw_low["level"])
            )
            if opp_break:
                ep = bar["close"]   # fill at the close of the breaking bar
                r  = (ep - active_trade["entry"]) / active_trade["risk"] if d == "long" \
                     else (active_trade["entry"] - ep) / active_trade["risk"]
                active_trade.update(exit_price=ep, exit_time=bar_dt,
                                    result="opp", r=r, win=(r > 0))
                trades.append(active_trade)
                active_trade = None
                in_trade     = False
                setup_used   = False
                reset_all()

                if opp_mode == "reverse":
                    # Arm the opposite bias from THIS break and let the normal
                    # CISD+FVG+entry logic build the reversal entry (mirrors FIX #3).
                    if d == "long":
                        bias           = BIAS_SHORT
                        recent_sw_high = None
                        reset_long_cisd(); reset_bear_run()
                    else:
                        bias          = BIAS_LONG
                        recent_sw_low = None
                        reset_short_cisd(); reset_bull_run()
                continue

        continue

    # ── Only evaluate inside session ──────────
    if not in_entry_session(bar_dt):
        continue

    # ─────────────────────────────────────────
    # CONTINUOUS CISD TRACKING
    # Gate: swing exists OR bias set
    # CISD updates only on new extreme
    # FVG persists unless range makes new extreme
    # ─────────────────────────────────────────

    # ── BULLISH CISD ──
    if bias != BIAS_SHORT and (recent_sw_low is not None or bias == BIAS_LONG) and not in_trade and not setup_used:
        if is_bearish(bar):
            prev_bearish = (i1 > 0 and is_bearish(df1.iloc[i1-1]))
            if bear_run_start is None or not prev_bearish:
                # FIX #1: anchor to the TRUE first candle of the consecutive
                # bearish run, even if tracking was inactive when it began.
                ts = i1; j = i1 - 1
                while j >= 0 and is_bearish(df1.iloc[j]):
                    ts = j; j -= 1
                bear_run_start = ts
                bear_run_open  = df1.iloc[ts]["open"]   # locked to first candle open
                bear_run_count = i1 - ts + 1
                seg            = df1.iloc[ts:i1+1]
                bear_run_sl    = float(seg["close"].min())
                bear_run_low   = float(seg["low"].min())
            else:
                bear_run_count += 1
                bear_run_sl     = min(bear_run_sl, bar["close"])
                bear_run_low    = min(bear_run_low, bar["low"])

            if bear_run_count >= 2:
                if cisd_long_low is None or bear_run_low < cisd_long_low:
                    # New extreme — update range and wipe FVG
                    cisd_long_start = bear_run_start
                    cisd_long_end   = i1
                    cisd_long_high  = bear_run_open
                    cisd_long_low   = bear_run_low
                    cisd_long_sl    = bear_run_sl
                    cisd_long_fvg_e = i1            # FIX #2: freeze FVG window to THIS run
                    reset_long_fvg()
                else:
                    # No new extreme — update end/sl only, keep level and FVG
                    cisd_long_end = i1
                    if bear_run_start == cisd_long_start:
                        cisd_long_fvg_e = i1        # extend only while the SAME run continues
                    if cisd_long_sl is not None:
                        cisd_long_sl = min(cisd_long_sl, bear_run_sl)
        else:
            # Non-bearish — reset run only, keep range and FVG
            reset_bear_run()

        # FVG scan — bounded to the CISD displacement run
        if cisd_long_start is not None and not fvg_long_valid:
            fvg = scan_fvg_long(cisd_long_start, cisd_long_fvg_e, i1)
            if fvg:
                fvg_long_stored = fvg
                fvg_long_valid  = True

    # ── BEARISH CISD ──
    if bias != BIAS_LONG and (recent_sw_high is not None or bias == BIAS_SHORT) and not in_trade and not setup_used:
        if is_bullish(bar):
            prev_bullish = (i1 > 0 and is_bullish(df1.iloc[i1-1]))
            if bull_run_start is None or not prev_bullish:
                # FIX #1: anchor to the TRUE first candle of the consecutive
                # bullish run, even if tracking was inactive when it began.
                ts = i1; j = i1 - 1
                while j >= 0 and is_bullish(df1.iloc[j]):
                    ts = j; j -= 1
                bull_run_start = ts
                bull_run_open  = df1.iloc[ts]["open"]   # locked to first candle open
                bull_run_count = i1 - ts + 1
                seg            = df1.iloc[ts:i1+1]
                bull_run_sl    = float(seg["close"].max())
                bull_run_high  = float(seg["high"].max())
            else:
                bull_run_count += 1
                bull_run_sl     = max(bull_run_sl, bar["close"])
                bull_run_high   = max(bull_run_high, bar["high"])

            if bull_run_count >= 2:
                if cisd_short_high is None or bull_run_high > cisd_short_high:
                    # New extreme — update range and wipe FVG
                    cisd_short_start = bull_run_start   # FIX: was i1 (asymmetry vs long side)
                    cisd_short_end   = i1
                    cisd_short_low   = bull_run_open
                    cisd_short_high  = bull_run_high
                    cisd_short_sl    = bull_run_sl
                    cisd_short_fvg_e = i1               # FIX #2: freeze FVG window to THIS run
                    reset_short_fvg()
                else:
                    # No new extreme — update end/sl only, keep level and FVG
                    cisd_short_end = i1
                    if bull_run_start == cisd_short_start:
                        cisd_short_fvg_e = i1           # extend only while the SAME run continues
                    if cisd_short_sl is not None:
                        cisd_short_sl = max(cisd_short_sl, bull_run_sl)
        else:
            reset_bull_run()

        if cisd_short_start is not None and not fvg_short_valid:
            fvg = scan_fvg_short(cisd_short_start, cisd_short_fvg_e, i1)
            if fvg:
                fvg_short_stored = fvg
                fvg_short_valid  = True

    # ─────────────────────────────────────────
    # 5m BREAK DETECTION → SET BIAS
    # ─────────────────────────────────────────
    if not in_trade and not setup_used:
        if recent_sw_low and bar["low"] < recent_sw_low["level"]:
            bias          = BIAS_LONG
            recent_sw_low = None
            reset_short_cisd(); reset_bull_run()    # FIX #3: low broken -> disarm pending short
        elif recent_sw_high and bar["high"] > recent_sw_high["level"]:
            bias           = BIAS_SHORT
            recent_sw_high = None
            reset_long_cisd(); reset_bear_run()     # FIX #3: high broken -> disarm pending long (look for shorts)

    # ─────────────────────────────────────────
    # ENTRY LOGIC
    # ─────────────────────────────────────────

    # ── LONG ──
    if (bias == BIAS_LONG
            and cisd_long_high is not None
            and fvg_long_valid
            and not in_trade
            and not setup_used
            and in_entry_session(bar_dt)):
        if bar["close"] > cisd_long_high:
            entry = bar["close"]
            sl    = cisd_long_sl
            risk  = entry - sl
            if risk > 0:
                active_trade = dict(
                    direction   = "long",
                    entry       = entry,
                    sl          = sl,
                    tp          = entry + risk * rr_input,
                    risk        = risk,
                    entry_time  = bar_dt,
                    cisd_level  = cisd_long_high,
                    fvg_c2_time = fvg_long_stored["candle2_time"],
                    fvg_low     = fvg_long_stored["fvg_low"],
                    fvg_high    = fvg_long_stored["fvg_high"],
                    year        = bar_dt.year,
                    month       = bar_dt.month,
                )
                in_trade   = True
                setup_used = True
                bias       = BIAS_NONE
                reset_all()

    # ── SHORT ──
    elif (bias == BIAS_SHORT
            and cisd_short_low is not None
            and fvg_short_valid
            and not in_trade
            and not setup_used
            and in_entry_session(bar_dt)):
        if bar["close"] < cisd_short_low:
            entry = bar["close"]
            sl    = cisd_short_sl
            risk  = sl - entry
            if risk > 0:
                active_trade = dict(
                    direction   = "short",
                    entry       = entry,
                    sl          = sl,
                    tp          = entry - risk * rr_input,
                    risk        = risk,
                    entry_time  = bar_dt,
                    cisd_level  = cisd_short_low,
                    fvg_c2_time = fvg_short_stored["candle2_time"],
                    fvg_low     = fvg_short_stored["fvg_low"],
                    fvg_high    = fvg_short_stored["fvg_high"],
                    year        = bar_dt.year,
                    month       = bar_dt.month,
                )
                in_trade   = True
                setup_used = True
                bias       = BIAS_NONE
                reset_all()

print(f"  Trades found: {len(trades):,}")
if len(trades) == 0:
    print("\n  !! 0 trades — verify data and session window.")
    sys.exit(1)

# ─────────────────────────────────────────────
# STATISTICS
# ─────────────────────────────────────────────
def calc_stats(tlist):
    if not tlist: return None
    n      = len(tlist)
    wins   = [t for t in tlist if t["win"]]
    losses = [t for t in tlist if not t["win"]]
    gp     = sum(t["r"] for t in wins)
    gl     = sum(abs(t["r"]) for t in losses)
    pf     = gp / gl if gl else float("inf")
    exp    = sum(t["r"] for t in tlist) / n
    res    = [t["win"] for t in tlist]
    mw=ml=cw=cl=0
    for r in res:
        if r:  cw+=1; cl=0
        else:  cl+=1; cw=0
        mw=max(mw,cw); ml=max(ml,cl)
    bal = 10_000.0
    for t in tlist:
        bal += bal * 0.01 * t["r"]
    return dict(n=n, wins=len(wins), losses=len(losses),
                win_pct=len(wins)/n*100, pf=pf, exp=exp,
                mw=mw, ml=ml, sim=bal)

by_year = defaultdict(list)
for t in trades:
    by_year[t["year"]].append(t)

# ─────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────
out_dir = f"backtestResults_{min(years_to_test)}to{max(years_to_test)}"
os.makedirs(out_dir, exist_ok=True)
print(f"\nSaving to: {os.path.abspath(out_dir)}")

lines = []
def sec(t):    lines.extend(["","="*50,f"  {t}","="*50])
def row(l,v):  lines.append(f"  {l:<34}{v}")

for yr in sorted(by_year):
    s = calc_stats(by_year[yr])
    if not s: continue
    sec(f"Year: {yr}")
    row("Total Trades",           s["n"])
    row("Wins / Losses",          f"{s['wins']} / {s['losses']}")
    row("Win %",                  f"{s['win_pct']:.1f}%")
    row("Profit Factor",          f"{s['pf']:.2f}" if s['pf']!=float("inf") else "∞")
    row("Expectancy (avg R)",     f"{s['exp']:.3f}R")
    row("Longest Win Streak",     s["mw"])
    row("Longest Loss Streak",    s["ml"])
    row("Sim Balance (1%,$10k)",  f"${s['sim']:,.2f}")

s = calc_stats(trades)
sec(f"ALL YEARS  ({min(years_to_test)}–{max(years_to_test)})")
row("Opposing-signal mode",   opp_mode)
row("Total Trades",           s["n"])
row("Wins / Losses",          f"{s['wins']} / {s['losses']}")
row("Win %",                  f"{s['win_pct']:.1f}%")
row("Profit Factor",          f"{s['pf']:.2f}" if s['pf']!=float("inf") else "∞")
row("Expectancy (avg R)",     f"{s['exp']:.3f}R")
row("Longest Win Streak",     s["mw"])
row("Longest Loss Streak",    s["ml"])
row("Sim Balance (1%,$10k)",  f"${s['sim']:,.2f}")

with open(os.path.join(out_dir,"stats.txt"),"w",encoding="utf-8") as f:
    f.write("\n".join(lines))
print("  stats.txt saved")

sorted_trades = sorted(trades, key=lambda t: t["entry_time"])
bal = 10_000.0; monthly = {}
for t in sorted_trades:
    bal += bal * 0.01 * t["r"]
    monthly[(t["year"],t["month"])] = bal

all_ym = sorted(monthly)
if all_ym:
    ym_list=[]; bal_list=[]; last=10_000.0
    yr,mo = all_ym[0][0],1
    while (yr,mo) <= all_ym[-1]:
        b = monthly.get((yr,mo), last)
        ym_list.append(f"{yr}-{mo:02d}"); bal_list.append(b)
        last=b; mo+=1
        if mo>12: mo=1; yr+=1

    fig,ax = plt.subplots(figsize=(14,6))
    ax.set_facecolor("#0d1117"); fig.patch.set_facecolor("#0d1117")
    x = range(len(ym_list))
    ax.plot(x, bal_list, color="#4af0a0", lw=1.5, zorder=3)
    ax.fill_between(x,10000,bal_list,
                    where=[b>=10000 for b in bal_list],color="#4af0a0",alpha=0.15)
    ax.fill_between(x,10000,bal_list,
                    where=[b<10000  for b in bal_list],color="#f04a4a",alpha=0.15)
    ax.axhline(10000,color="#555",lw=0.8,ls="--")
    step=max(1,len(ym_list)//20)
    ax.set_xticks(list(x)[::step])
    ax.set_xticklabels(ym_list[::step],rotation=45,ha="right",color="#aaa",fontsize=7)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_:f"${v:,.0f}"))
    ax.tick_params(axis="y",colors="#aaa")
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_title(f"Equity Curve  (1% risk · $10,000 start · opp={opp_mode})",color="#eee",fontsize=13,pad=12)
    ax.set_xlabel("Month",color="#888",fontsize=9)
    ax.set_ylabel("Account Balance",color="#888",fontsize=9)
    ax.grid(axis="y",color="#1e2530",lw=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir,"equity_curve.png"),dpi=150,
                bbox_inches="tight",facecolor="#0d1117")
    plt.close()
    print("  equity_curve.png saved")

t26 = [t for t in trades if t["year"]==2026]
if t26:
    sample = random.sample(t26, min(20,len(t26)))
    rows = []
    for t in sample:
        rows.append({
            "Entry Time":       t["entry_time"].strftime("%Y-%m-%d %H:%M"),
            "Direction":        t["direction"].upper(),
            "W/L":              "W" if t["win"] else "L",
            "Result":           t.get("result",""),
            "CISD Level":       round(t["cisd_level"],5),
            "FVG Candle2 Time": pd.Timestamp(t["fvg_c2_time"]).strftime("%Y-%m-%d %H:%M"),
            "Entry Price":      round(t["entry"],5),
            "TP Price":         round(t["tp"],5),
            "SL Price":         round(t["sl"],5),
            "R":                round(t["r"],2),
        })
    pd.DataFrame(rows).to_csv(os.path.join(out_dir,"examples_2026.csv"),index=False)
    print(f"  examples_2026.csv saved  ({len(sample)} trades)")
else:
    print("  No 2026 trades — examples_2026.csv skipped")

print(f"\n✓ Done.  Output: {os.path.abspath(out_dir)}")
inp = input("\nRun again? (yes/no): ").strip().lower()
if inp not in ("yes","y"):
    sys.exit(0)