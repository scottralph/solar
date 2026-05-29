# solar

A command-line tool that generates a 2–3 day HF radio propagation forecast by gathering real-time and forecast data from three public space weather sources.

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

## What the report contains

- **Current conditions** — SFI, Kp, A-index, X-ray flux class, solar wind speed/density, IMF Bz/Bt/By with 30-minute trend detection, DST index
- **Propagation summary** — plain-English assessment of each indicator and its HF impact
- **3-day event probabilities** — R1 radio blackout and S1 radiation storm percentages
- **3-day Kp breakdown** — hourly Kp forecast table (8 × 3-hour slots per day)
- **Solar wind & geospace forecast** — narrative outlook extracted from the NOAA forecast discussion
- **Active alerts** — any current NOAA watches, warnings, or alerts
- **Forecast discussion** — full NOAA forecaster narrative covering solar activity, energetic particles, solar wind, and geospace sections

## Example output

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
