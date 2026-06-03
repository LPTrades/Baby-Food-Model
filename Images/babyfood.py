"""
CISD + FVG Backtest  — NQ 1m + 5m
Rebuilt from Pine Script source of truth.
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

# ─────────────────────────────────────────────
# CANDLE HELPERS
# Pine uses strict: close < open = bearish, close > open = bullish
# ─────────────────────────────────────────────
def is_bearish(bar): return bar["close"] < bar["open"]
def is_bullish(bar): return bar["close"] > bar["open"]

# ─────────────────────────────────────────────
# 5M SWING DETECTION
# Swing low  : b.low < a.low AND b.low < c.low  → level = b.low
# Swing high : b.high > a.high AND b.high > c.high → level = b.high
# Confirmed on close of 3rd candle (c)
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
def in_session(dt):
    return sess_start_t <= dt.time() <= sess_end_t

force_close_time = dtime(15, 45)

# ─────────────────────────────────────────────
# FVG SCAN — matches Pine Script exactly
#
# For LONGS (bearish CISD):
#   Bearish FVG: c1.low > c3.high  → fvg_high=c1.low, fvg_low=c3.high
#   candle 2 must be in [cisd_start_idx .. cisd_end_idx+5]
#
# For SHORTS (bullish CISD):
#   Bullish FVG: c3.low > c1.high  → fvg_high=c3.low, fvg_low=c1.high
#   candle 2 must be in [cisd_start_idx .. cisd_end_idx+5]
#
# Returns the FIRST (earliest) valid FVG found.
# ─────────────────────────────────────────────
def scan_fvg(cisd_start, cisd_end, direction):
    """
    Scans the window where candle2 index is in [cisd_start, cisd_end+5].
    Returns dict or None.
    """
    n = len(df1)
    c2_min = cisd_start
    c2_max = min(cisd_end + 5, n - 2)

    for c2_idx in range(c2_min, c2_max + 1):
        c1_idx = c2_idx - 1
        c3_idx = c2_idx + 1
        if c1_idx < 0 or c3_idx >= n:
            continue
        c1 = df1.iloc[c1_idx]
        c3 = df1.iloc[c3_idx]

        if direction == "bull":
            # Bearish FVG inside bearish CISD → for LONG entries
            # c1.low > c3.high
            if c1["low"] > c3["high"]:
                return {
                    "fvg_high":      c1["low"],
                    "fvg_low":       c3["high"],
                    "candle2_time":  df1.iloc[c2_idx]["datetime"],
                }
        else:
            # Bullish FVG inside bullish CISD → for SHORT entries
            # c3.low > c1.high
            if c3["low"] > c1["high"]:
                return {
                    "fvg_high":      c3["low"],
                    "fvg_low":       c1["high"],
                    "candle2_time":  df1.iloc[c2_idx]["datetime"],
                }
    return None

# ─────────────────────────────────────────────
# MAIN BACKTEST
# ─────────────────────────────────────────────
trades = []

BIAS_NONE  =  0
BIAS_LONG  =  1
BIAS_SHORT = -1

bias        = BIAS_NONE
setup_used  = False
in_trade    = False
active_trade= None

recent_sw_low  = None
recent_sw_high = None

# CISD state — mirrors Pine vars
cisd_start_idx  = None
cisd_end_idx    = None
cisd_range_high = None   # open of first candle (top of bearish CISD / bottom check for bullish)
cisd_range_low  = None   # tracks new lower lows / higher highs
cisd_sl_level   = None   # lowest close (long) / highest close (short)
fvg_valid       = False
stored_fvg      = None

# Run tracking — mirrors bear_run / bull_run in Pine
run_start = None
run_count = 0
run_open  = None
run_sl    = None         # lowest close (long) or highest close (short)

sq_ptr = 0

def reset_cisd_state():
    global cisd_start_idx, cisd_end_idx, cisd_range_high, cisd_range_low
    global cisd_sl_level, fvg_valid, stored_fvg
    global run_start, run_count, run_open, run_sl
    cisd_start_idx = cisd_end_idx = cisd_range_high = cisd_range_low = cisd_sl_level = None
    fvg_valid  = False
    stored_fvg = None
    run_start  = None
    run_count  = 0
    run_open   = run_sl = None

def reset_run():
    global run_start, run_count, run_open, run_sl
    run_start = None
    run_count = 0
    run_open  = run_sl = None

n1 = len(df1)
print("\nRunning backtest...")

for i1 in range(n1):
    bar    = df1.iloc[i1]
    bar_dt = bar["datetime"]
    bar_t  = bar_dt.time()

    # ── Advance swing queue ────────────────────
    while sq_ptr < len(swing_events):
        ev = swing_events[sq_ptr]
        if ev["confirmed_time"] <= bar_dt:
            if ev["type"] == "swing_low":
                recent_sw_low  = {"level": ev["level"]}
            else:
                recent_sw_high = {"level": ev["level"]}
            sq_ptr += 1
        else:
            break

    # ── New session reset (mirrors Pine new_session_1m) ──
    # Reset everything at start of each trading day
    if bar_t == sess_start_t or (i1 > 0 and df1.iloc[i1-1]["datetime"].date() != bar_dt.date()
                                  and in_session(bar_dt)):
        if not in_trade:
            bias       = BIAS_NONE
            setup_used = False
            reset_cisd_state()

    # ── Force-close 15:45 ─────────────────────
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
        reset_cisd_state()
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
            setup_used   = False          # allow fresh setup after next swing break
            reset_cisd_state()
        continue

    # ── Only evaluate inside session ──────────
    if not in_session(bar_dt):
        continue

    # ── 5m Break detection ────────────────────
    # Mirrors Pine: sets bias and resets CISD/FVG state
    if not in_trade and not setup_used:
        if recent_sw_low and bar["low"] < recent_sw_low["level"]:
            bias           = BIAS_LONG
            recent_sw_low  = None
            reset_cisd_state()
        elif recent_sw_high and bar["high"] > recent_sw_high["level"]:
            bias           = BIAS_SHORT
            recent_sw_high = None
            reset_cisd_state()

    # ── CISD tracking ─────────────────────────
    if bias == BIAS_LONG and not in_trade and not setup_used and in_session(bar_dt):
        if is_bearish(bar):
            prev_bearish = (i1 > 0 and is_bearish(df1.iloc[i1-1]))
            if run_start is None or not prev_bearish:
                # Start new bearish run
                run_start = i1
                run_open  = bar["open"]
                run_sl    = bar["close"]
                run_count = 1
            else:
                # Extend run
                run_count += 1
                run_sl = min(run_sl, bar["close"])
                # Update CISD range only if new lower low
                if cisd_range_low is None or bar["low"] < cisd_range_low:
                    cisd_start_idx  = run_start
                    cisd_end_idx    = i1
                    cisd_range_high = run_open
                    cisd_range_low  = bar["low"]
                    cisd_sl_level   = run_sl
                    # Rescan FVG on range extension
                    fvg_valid  = False
                    stored_fvg = None

            # Capture CISD range on reaching 2 candles
            if run_count >= 2 and cisd_start_idx is None:
                cisd_start_idx  = run_start
                cisd_end_idx    = i1
                cisd_range_high = run_open
                cisd_range_low  = bar["low"]
                cisd_sl_level   = run_sl

        else:
            # Non-bearish — reset run tracker (but keep stored CISD range)
            reset_run()

        # FVG scan each bar while CISD range exists and FVG not yet found
        if cisd_start_idx is not None and not fvg_valid and not in_trade:
            fvg = scan_fvg(cisd_start_idx, cisd_end_idx, "bull")
            if fvg:
                stored_fvg = fvg
                fvg_valid  = True

        # CISD confirmation check
        if cisd_range_high is not None and fvg_valid and is_bullish(bar):
            if bar["close"] > cisd_range_high:
                entry = bar["close"]
                sl    = cisd_sl_level
                risk  = entry - sl
                if risk > 0:
                    active_trade = dict(
                        direction   = "long",
                        entry       = entry,
                        sl          = sl,
                        tp          = entry + risk * rr_input,
                        risk        = risk,
                        entry_time  = bar_dt,
                        cisd_level  = cisd_range_high,
                        fvg_c2_time = stored_fvg["candle2_time"],
                        fvg_low     = stored_fvg["fvg_low"],
                        fvg_high    = stored_fvg["fvg_high"],
                        year        = bar_dt.year,
                        month       = bar_dt.month,
                    )
                    in_trade   = True
                    setup_used = True
                    bias       = BIAS_NONE
                    reset_cisd_state()

    elif bias == BIAS_SHORT and not in_trade and not setup_used and in_session(bar_dt):
        if is_bullish(bar):
            prev_bullish = (i1 > 0 and is_bullish(df1.iloc[i1-1]))
            if run_start is None or not prev_bullish:
                run_start = i1
                run_open  = bar["open"]
                run_sl    = bar["close"]
                run_count = 1
            else:
                run_count += 1
                run_sl = max(run_sl, bar["close"])
                if cisd_range_high is None or bar["high"] > cisd_range_high:
                    cisd_start_idx  = run_start
                    cisd_end_idx    = i1
                    cisd_range_low  = run_open
                    cisd_range_high = bar["high"]
                    cisd_sl_level   = run_sl
                    fvg_valid  = False
                    stored_fvg = None

            if run_count >= 2 and cisd_start_idx is None:
                cisd_start_idx  = run_start
                cisd_end_idx    = i1
                cisd_range_low  = run_open
                cisd_range_high = bar["high"]
                cisd_sl_level   = run_sl

        else:
            reset_run()

        if cisd_start_idx is not None and not fvg_valid and not in_trade:
            fvg = scan_fvg(cisd_start_idx, cisd_end_idx, "short")
            if fvg:
                stored_fvg = fvg
                fvg_valid  = True

        if cisd_range_low is not None and fvg_valid and is_bearish(bar):
            if bar["close"] < cisd_range_low:
                entry = bar["close"]
                sl    = cisd_sl_level
                risk  = sl - entry
                if risk > 0:
                    active_trade = dict(
                        direction   = "short",
                        entry       = entry,
                        sl          = sl,
                        tp          = entry - risk * rr_input,
                        risk        = risk,
                        entry_time  = bar_dt,
                        cisd_level  = cisd_range_low,
                        fvg_c2_time = stored_fvg["candle2_time"],
                        fvg_low     = stored_fvg["fvg_low"],
                        fvg_high    = stored_fvg["fvg_high"],
                        year        = bar_dt.year,
                        month       = bar_dt.month,
                    )
                    in_trade   = True
                    setup_used = True
                    bias       = BIAS_NONE
                    reset_cisd_state()

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
# OUTPUT FOLDER
# ─────────────────────────────────────────────
out_dir = f"backtestResults_{min(years_to_test)}to{max(years_to_test)}"
os.makedirs(out_dir, exist_ok=True)
print(f"\nSaving to: {os.path.abspath(out_dir)}")

# ── stats.txt ────────────────────────────────
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

# ── equity_curve.png ─────────────────────────
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
    ax.set_title("Equity Curve  (1% risk · $10,000 start)",color="#eee",fontsize=13,pad=12)
    ax.set_xlabel("Month",color="#888",fontsize=9)
    ax.set_ylabel("Account Balance",color="#888",fontsize=9)
    ax.grid(axis="y",color="#1e2530",lw=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir,"equity_curve.png"),dpi=150,
                bbox_inches="tight",facecolor="#0d1117")
    plt.close()
    print("  equity_curve.png saved")

# ── examples_2026.csv ────────────────────────
t26 = [t for t in trades if t["year"]==2026]
if t26:
    sample = random.sample(t26, min(20,len(t26)))
    rows = []
    for t in sample:
        rows.append({
            "Entry Time":       t["entry_time"].strftime("%Y-%m-%d %H:%M"),
            "Direction":        t["direction"].upper(),
            "W/L":              "W" if t["win"] else "L",
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