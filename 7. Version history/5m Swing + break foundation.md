```
//@version=5
indicator("5m Swings + Broken Levels", overlay=true, max_lines_count=20)

// ============================================================
// SETTINGS
// ============================================================
session_input = input.session("0930-1200", "Session")

// ============================================================
// SESSION FILTER
// ============================================================
in_session = not na(time("5", session_input, "America/New_York"))
session_end_time = timestamp("America/New_York", year, month, dayofmonth, 12, 0, 0)
new_session = in_session and not in_session[1]

// ============================================================
// 5m DATA — pull time[1] alongside price so lines anchor to
// the actual 5m pivot bar, not the current 1m bar
// ============================================================
[h,  l ]      = request.security(syminfo.tickerid, "5", [high,    low   ], lookahead=barmerge.lookahead_off)
[h1, l1, t1]  = request.security(syminfo.tickerid, "5", [high[1], low[1], time[1]], lookahead=barmerge.lookahead_off)
[h2, l2]      = request.security(syminfo.tickerid, "5", [high[2], low[2]], lookahead=barmerge.lookahead_off)

// ============================================================
// SWING DETECTION (immediate left + right candle rule)
// ============================================================
is_swing_high = h1 > h2 and h1 > h
is_swing_low  = l1 < l2 and l1 < l

// Only fire once per 5m bar (avoid re-trigger across the 5 underlying 1m bars)
new_5m_bar = ta.change(t1) != 0

// ============================================================
// STATE
// ============================================================
var float recent_swing_high       = na
var float recent_swing_low        = na
var int   recent_swing_high_time  = na
var int   recent_swing_low_time   = na

var float broken_swing_high       = na
var float broken_swing_low        = na
var int   broken_swing_high_time  = na
var int   broken_swing_low_time   = na

var line  recent_high_line  = na
var line  recent_low_line   = na
var line  broken_high_line  = na
var line  broken_low_line   = na

// ============================================================
// RESET ON NEW SESSION
// ============================================================
if new_session
    recent_swing_high      := na
    recent_swing_low       := na
    recent_swing_high_time := na
    recent_swing_low_time  := na
    broken_swing_high      := na
    broken_swing_low       := na
    broken_swing_high_time := na
    broken_swing_low_time  := na
    line.delete(recent_high_line)
    line.delete(recent_low_line)
    line.delete(broken_high_line)
    line.delete(broken_low_line)
    recent_high_line := na
    recent_low_line  := na
    broken_high_line := na
    broken_low_line  := na

// ============================================================
// CAPTURE NEW SWINGS (anchored to 5m pivot bar's time)
// ============================================================
if in_session and new_5m_bar and is_swing_high
    recent_swing_high      := h1
    recent_swing_high_time := t1
    line.delete(recent_high_line)
    recent_high_line := line.new(recent_swing_high_time, recent_swing_high, session_end_time, recent_swing_high, xloc=xloc.bar_time, color=color.red, style=line.style_dashed, width=1)

if in_session and new_5m_bar and is_swing_low
    recent_swing_low      := l1
    recent_swing_low_time := t1
    line.delete(recent_low_line)
    recent_low_line := line.new(recent_swing_low_time, recent_swing_low, session_end_time, recent_swing_low, xloc=xloc.bar_time, color=color.green, style=line.style_dashed, width=1)

// ============================================================
// BREAK DETECTION (uses current chart's high/low — 1m if on 1m)
// ============================================================
if in_session and not na(recent_swing_high) and high > recent_swing_high
    broken_swing_high      := recent_swing_high
    broken_swing_high_time := recent_swing_high_time
    line.delete(broken_high_line)
    broken_high_line := line.new(broken_swing_high_time, broken_swing_high, session_end_time, broken_swing_high, xloc=xloc.bar_time, color=color.red, style=line.style_dotted, width=1)
    line.delete(recent_high_line)
    recent_high_line  := na
    recent_swing_high := na

if in_session and not na(recent_swing_low) and low < recent_swing_low
    broken_swing_low      := recent_swing_low
    broken_swing_low_time := recent_swing_low_time
    line.delete(broken_low_line)
    broken_low_line := line.new(broken_swing_low_time, broken_swing_low, session_end_time, broken_swing_low, xloc=xloc.bar_time, color=color.green, style=line.style_dotted, width=1)
    line.delete(recent_low_line)
    recent_low_line  := na
    recent_swing_low := na

// ============================================================
// LEGEND
// Red  dashed = most recent unbroken 5m swing high
// Green dashed = most recent unbroken 5m swing low
// Red  dotted = most recent BROKEN swing high
// Green dotted = most recent BROKEN swing low
// ============================================================

```