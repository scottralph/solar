# Solar — Radio Condition Forecaster

Generates a 2–3 day radio condition prediction by gathering data from multiple external sources.

## Primary usage

**`/two-day-outlook`** — the main command. Fetches fresh solar data and produces a day-by-day narrative operating forecast for the next two days: band conditions, Kp by UT slot, solar wind drivers, Bz outlook, flare risk, and key watch points. Use this for daily planning.

**`/solar`** — fetches and displays the full raw forecast report (current conditions, Kp table, event probabilities, forecast discussion). Use this when you want the underlying data.

## Goal

Produce a daily forecast report summarising expected HF/VHF propagation conditions, solar activity, and geomagnetic indices.

## Data sources

To be identified by the user.

## Project structure

```
solar/
├── CLAUDE.md
├── .gitignore
└── (source files to be added)
```
