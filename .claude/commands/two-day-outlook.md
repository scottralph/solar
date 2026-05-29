---
description: Generate a two-day HF radio operating forecast with day-by-day narrative
allowed-tools: [Bash]
---

Run the solar forecast to fetch fresh data:

```bash
python3 main.py
```

Using that output, produce a two-day operating forecast. The two days are the second and third days covered by the 3-day Kp forecast table (i.e. tomorrow and the day after).

---

**Output format — follow this exactly:**

DD MON (day label taken from the Kp forecast table column)

- Solar flux (SFI NNN): Band condition summary — which bands most reliable, which unlikely to be consistently open.
- Kp: Summarise the Kp slots for this day from the forecast table. Note the peak value and which UT slot it falls in. Give an overall geomagnetic assessment for the day.
- Solar wind: Narrative on solar wind drivers for this day (HSS, CME, quiet). Expected speed range.
- Bz: Outlook for Bz behaviour and what it means for coupling. If no numerical forecast, say so and explain what to watch for.
- Flare risk: R1 blackout probability, which active regions are responsible, plain-language risk framing.
- Radiation storms: S1 probability and whether it warrants attention.
- Overall: One or two sentences — is it a good operating day, when is it best, any caveats.

---
DD MON (second day)

- Solar flux (SFI): Note if any change from the first day; same band conditions or different.
- Kp: Summarise the Kp slots. Note the peak and UT timing. If Kp reaches 4+, call out which latitude paths will be affected and from what time UTC.
- Solar wind: Narrative on solar wind drivers. If a new HSS or CME arrival is expected, say when and what it implies for wind speed.
- Bz: If a HSS or CME arrival is expected, explain the typical Bz behaviour and what a sustained southward turning would mean.
- Geomagnetic storm probabilities: If elevated Kp is forecast, include a latitudinal breakdown (mid-latitude vs high-latitude active/G1/G2+ chances derived from the forecast text).
- Flare risk: R1 blackout probability.
- Overall: One or two sentences — note if conditions degrade through the day, and from roughly what UT time.

---
KEY WATCH POINTS

Numbered list of the two or three most operationally significant things to monitor over the two-day period — specific events (CME arrival window, HSS onset timing, active regions still on disk). Be specific about UT timing where the forecast gives it.

---

Write in the style of a knowledgeable amateur radio operator briefing other operators. Be specific with UT times. Do not add any preamble or closing text — output the two-day report only.
