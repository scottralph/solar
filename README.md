# solar

A command-line tool that generates a 2–3 day HF radio propagation forecast by gathering real-time and forecast data from three public space weather sources.

## Primary usage — `/two-day-outlook`

The main entry point is the Claude Code slash command `/two-day-outlook`. It fetches fresh solar data and produces a plain-English, day-by-day operating forecast for the next two days — band conditions, Kp by UT slot, solar wind drivers, Bz outlook, flare risk, and key watch points.

Open this project in [Claude Code](https://claude.ai/code) and type:

```
/two-day-outlook
```

### Example output

Generated 2026-05-29, covering 30–31 May:

```
30 May

- Solar flux (SFI 106): Fair. 20m and lower bands most reliable; 17m marginal and a
  stretch on any given path. 15m and above unlikely to be consistently open.
- Kp: Quiet through the morning — 1.33 in both the 06–09 and 09–12 UT slots, the
  cleanest part of the day. Rises to 2.67 at 12–15 UT and peaks at 3.00 in both the
  18–21 and 21–00 UT slots. Geomagnetic field quiet to unsettled all day — no
  meaningful disruption to mid-latitude paths; polar routes may see minor softening
  in the evening slots.
- Solar wind: Weak -CH HSS influences waning through 30 May. A glancing CME (departed
  Sun 26 May) could arrive at any point during the day — if it does, expect a brief
  speed enhancement above the current 400–450 km/s baseline. Forecasters characterise
  the potential effect as minor and short-lived.
- Bz: No numerical forecast available for 30 May. Bz is currently at -0.1 nT —
  effectively neutral. If the CME arrives, watch for a transient southward excursion;
  the trailing edge of the current HSS can also produce variable Bz dips. Nothing
  alarming is expected, but keep an eye on live feeds if Kp starts climbing
  unexpectedly.
- Flare risk: 40% chance of an R1 radio blackout. Regions 4452 (anti-Hale, beta-gamma,
  approaching the west limb) and 4455 (beta-gamma, rising in the east) are the active
  sources. A brief sunlit-hemisphere blackout is plausible but not the most likely
  outcome.
- Radiation storms: 5% S1 — background, no concern.
- Overall: A good operating day, particularly in the morning UT window (00–12 UT). The
  slight Kp rise in the afternoon and evening is minor. The main wildcard is CME arrival
  timing — if it shows up, conditions should recover within a few hours.

---

31 May

- Solar flux (SFI): No change expected — SFI 106, same fair conditions. Band picture
  identical to 30 May; 20m and lower the go-to bands.
- Kp: Starts moderate (3.00 at 00–03 UT) and holds in the 1.67–2.33 range through
  mid-morning. The step-change comes at 12–15 UT (3.33), accelerating to a peak of 4.00
  in the 18–21 UT slot, then 3.67 at 21–00 UT. From 15 UT onwards, paths through
  latitudes above ~50° will feel increasing absorption and auroral degradation. By
  18–21 UT, polar and transpolar routes are likely significantly impacted; mid-latitude
  paths on the higher end of the band will also show some softening.
- Solar wind: The main event of the two-day period. A new -CH HSS onset is expected on
  31 May, combined with possible glancing influences from slow eruptions that left the
  Sun on 27–28 May. Wind speed is likely accelerating through the day — probably
  climbing well above the 450 km/s baseline by late afternoon UT. Sustained elevated
  wind from multiple drivers raises the risk of prolonged geomagnetic activity.
- Bz: This is the critical variable to watch on 31 May. HSS arrivals typically produce
  a period of fluctuating and potentially sustained southward Bz as the stream
  interaction region passes. A sustained southward excursion to -5 nT or deeper for
  several hours is what would push Kp to 4+ and potentially trigger a G1 storm. Monitor
  live Bz closely from 12–15 UT; if it turns and holds southward, deterioration will
  follow within 1–2 hours.
- Geomagnetic storm probabilities: With Kp peaking at 4.00 and active conditions
  described as likely: mid-latitude paths face around 30–40% chance of active conditions
  and ~10–15% chance of a brief G1 storm; high-latitude paths carry substantially higher
  risk — meaningful probability of G1 and a real chance of G1–G2 if Bz cooperates with
  the combined HSS and CME glancing blow.
- Flare risk: 40% R1 blackout risk — same as 30 May. Regions 4452 and 4455 still the
  primary candidates.
- Overall: 31 May morning UT (00–12) is the window to exploit — conditions comparable
  to 30 May. From 15 UT expect a progressive deterioration; by 18–21 UT plan for active
  conditions at minimum. An M-class flare on top of geomagnetic activity would be a
  double hit.

---

KEY WATCH POINTS

1. CME arrival 30 May — the 26 May CME could deliver a glancing blow at any time during
   30 May; watch live Kp and Bz for a sudden southward dip and Kp jump — recovery
   expected within a few hours if it arrives.
2. HSS onset 31 May from ~12–15 UT — the main event; watch ACE/DSCOVR for solar wind
   speed acceleration and Bz for a sustained southward turn; the 18–21 UT slot (Kp 4.00)
   is the highest-risk window for path degradation above 50° latitude.
3. Regions 4452 and 4455 both days — both remain on disk and M-class capable; a
   significant flare during already-elevated geomagnetic conditions on 31 May would
   compound the impact — if propagation suddenly drops on the sunlit side, check X-ray
   flux before assuming it's geomagnetic.
```

## Raw forecast — `/solar`

For the full underlying data (current conditions, Kp table, event probabilities, full NOAA discussion), use the `/solar` slash command, or run directly:

```bash
python3 main.py
```

See the [Example output](#example-output-solar) section below for a sample.

## Data sources

| Source | Method | Used for |
|--------|--------|----------|
| [NOAA SWPC](https://www.swpc.noaa.gov/) | REST API | Solar flux, Kp, X-ray flux, solar wind, IMF, alerts, 3-day forecast |
| [spaceweather.com](https://spaceweather.com/) | Scraping | Headline / current event summary |
| [spaceweatherlive.com](https://www.spaceweatherlive.com/) | Scraping | Forecast discussion, solar wind & geospace outlook |

## Installation

```bash
git clone https://github.com/scottralph/solar.git
cd solar
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Activate the virtual environment (first time per session)
source .venv/bin/activate

# Generate the forecast report
python main.py

# Dump all raw fetched data as JSON (useful for debugging)
python main.py --json
```

The report is printed to stdout. Pipe it to a pager or file as needed:

```bash
python main.py | less
python main.py > forecast.txt
```

## Claude Code slash commands

Two slash commands are included for use with [Claude Code](https://claude.ai/code):

| Command | What it does |
|---------|-------------|
| `/two-day-outlook` | **Primary.** Fetches fresh data and produces a day-by-day narrative forecast for the next two days. |
| `/solar` | Fetches and displays the full raw report — current conditions, Kp table, event probabilities, and forecast discussion. |

Both work out of the box — no extra setup needed beyond the normal installation above.

## What the report contains

- **Current conditions** — SFI, Kp, A-index, X-ray flux class, solar wind speed/density, IMF Bz/Bt/By with 30-minute trend detection, DST index
- **Propagation summary** — plain-English assessment of each indicator and its HF impact
- **3-day event probabilities** — R1 radio blackout and S1 radiation storm percentages
- **3-day Kp breakdown** — hourly Kp forecast table (8 × 3-hour slots per day)
- **Solar wind & geospace forecast** — narrative outlook extracted from the NOAA forecast discussion
- **Active alerts** — any current NOAA watches, warnings, or alerts
- **Forecast discussion** — full NOAA forecaster narrative covering solar activity, energetic particles, solar wind, and geospace sections

## Example output — `/solar` {#example-output-solar}

Generated 2026-05-29 covering the 30–31 May weekend:

```
RADIO CONDITION FORECAST — generated 2026-05-29 18:54Z
Sources: NOAA SWPC · spaceweather.com · spaceweatherlive.com

============================================================
  CURRENT CONDITIONS
============================================================
  F10.7 Solar Flux (SFI):        106.0 sfu  [fair]
  Planetary Kp Index:            2.67  [unsettled]
    NOAA A-index:                13
  X-ray flux (0.1–0.8 nm):       B-class (low)
  Solar wind speed:              438 km/s  [DSCOVR]
  Solar wind density:            10.48 p/cm³
  IMF Bz (GSM):                  +1.3 nT (weakly northward)
  IMF Bt (total):                6.8 nT  By=-4.4 nT
  DST index:                     unknown

============================================================
  PROPAGATION SUMMARY
============================================================
  Solar flux (SFI 106) is fair — expect a typical MUF; 20m
  and lower bands most reliable.

  Kp 2.67 — geomagnetic field quiet. No disruption expected.

  IMF Bz northward (+1.3 nT) — no significant magnetospheric
  coupling; favourable.

  Solar wind moderate (438 km/s) — nominal; not a concern on
  its own.

  Solar wind density elevated (10.5 p/cm³) — worth
  monitoring alongside Bz.

  X-ray flux low (A/B class) — no flare-related HF impact.


  Past 24h:  minor. Radio blackouts reaching the R1 level occurred.
  Next 24h:  No storms predicted

============================================================
  3-DAY EVENT PROBABILITIES  (from NOAA 3-day forecast)
============================================================
  Day            R1 Blackout%   S1 Radiation%
  --------------------------------------------
  May 29                   40               5
  May 30                   40               5
  May 31                   40               5

============================================================
  Kp FORECAST (3-DAY)
============================================================
  NOAA Kp index breakdown May 29-May 31 2026
               May 29       May 30       May 31
  00-03UT       2.67         2.33         3.00
  03-06UT       3.00         2.00         2.33
  06-09UT       2.33         1.33         2.33
  09-12UT       3.67         1.33         1.67
  12-15UT       2.00         2.67         3.33
  15-18UT       2.33         2.33         2.67
  18-21UT       2.67         3.00         4.00
  21-00UT       3.67         3.00         3.67

============================================================
  SOLAR WIND & GEOSPACE FORECAST (3-DAY)
============================================================
  Solar Wind:
    Mild enhancements due to weak -CH HSS influences are
    likely to persist through 29 May. Further enhancements
    are possible on 30 May due to a CME that departed the
    Sun on 26 May. Additional solar wind enhancements are
    anticipated on 31 May due to the onset of a new -CH HSS,
    combined with possible glancing influences from the slow
    eruptions that departed the Sun on 27 and 28 May.

  Geospace / Geomagnetic:
    Geomagnetic field conditions are anticipated to be at
    quiet to unsettled levels 29–30 May, with a chance for
    isolated active periods due to waning -CH HSS effects
    and potential glancing CME influences. Active conditions
    are likely on 31 May in response to the combined onset
    of the new -CH HSS and glancing CME influences.

============================================================
  FORECAST DISCUSSION
============================================================
  -- SOLAR ACTIVITY --

  24 h Summary Solar activity reached moderate levels with
  an M1.1/sf at 29/0704 UTC from Region 4455 (N15E52,
  Eho/beta-gamma), which was the main flare factory this
  last 24 hours, with the occasional flare from Region 4452
  (N10W48, Dai/beta-gamma).

  ...

  -- FORECAST --

  Solar activity is expected to be at low to moderate levels
  through 31 May. There remains a chance for isolated
  M-class flares (R1-R2/Minor-Moderate), driven primarily by
  Regions 4452 and 4455.

  -- SOLAR WIND --

  ...

  -- FORECAST --

  Mild enhancements due to weak -CH HSS influences are
  likely to persist through 29 May. Further enhancements are
  possible on 30 May due to a CME that departed the Sun on
  26 May. Additional solar wind enhancements are anticipated
  on 31 May due to the onset of a new -CH HSS, combined with
  possible glancing influences from the slow eruptions that
  departed the Sun on 27 and 28 May.

  -- GEOSPACE --

  ...

  -- FORECAST --

  Geomagnetic field conditions are anticipated to be at
  quiet to unsettled levels 29–30 May, with a chance for
  isolated active periods due to waning -CH HSS effects and
  potential glancing CME influences. Active conditions are
  likely on 31 May in response to the combined onset of the
  new -CH HSS and glancing CME influences.

============================================================
  All times UTC.  Data sourced from public feeds.
============================================================
```

## Glossary

| Term | Meaning |
|------|---------|
| SFI / F10.7 | Solar Flux Index — 10.7 cm radio emission from the Sun. Higher = more ionisation = better HF propagation. |
| Kp | Planetary geomagnetic index, 0–9. Above 4 means active conditions; polar paths affected from ~5 upward. |
| A-index | Daily geomagnetic activity index (0–400). Derived from Kp. |
| IMF Bz | North-south component of the interplanetary magnetic field. Southward (negative) Bz couples with Earth's magnetosphere and drives geomagnetic storms. |
| IMF Bt | Total strength of the interplanetary magnetic field in nanoteslas. |
| DST | Disturbance Storm Time index. Negative values indicate a geomagnetic storm in progress. |
| R1–R5 | NOAA radio blackout scale. R1 (minor) to R5 (extreme). Caused by X-ray flux from solar flares. |
| S1–S5 | NOAA solar radiation storm scale. |
| G1–G5 | NOAA geomagnetic storm scale. G1 = Kp 5, G5 = Kp 9. |
| HSS | High-Speed Stream — fast solar wind from a coronal hole. Can cause sustained geomagnetic activity on arrival. |
| CME | Coronal Mass Ejection — a large eruption of plasma from the Sun. Can cause rapid geomagnetic storm onset. |
| MUF | Maximum Usable Frequency — the highest frequency that will reliably reflect off the ionosphere on a given path. |
