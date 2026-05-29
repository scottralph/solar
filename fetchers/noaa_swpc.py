"""Fetches space weather data from NOAA SWPC public endpoints."""

import re
from datetime import datetime, timezone

import requests

BASE = "https://services.swpc.noaa.gov"
TIMEOUT = 15


def _get_json(path: str) -> list | dict:
    r = requests.get(f"{BASE}{path}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _get_text(path: str) -> str:
    r = requests.get(f"{BASE}{path}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------
# Individual fetchers
# ---------------------------------------------------------------------------

def fetch_wwv() -> dict:
    """Parse WWV geophysical alert text into a dict."""
    text = _get_text("/text/wwv.txt")
    data = {"raw": text}

    patterns = {
        "solar_flux": r"Solar flux (\d+)",
        "a_index": r"A-index (\d+)",
        "k_index": r"K-index (\d+)",
        "solar_flux_forecast": r"(?:Solar flux is expected|Solar Flux forecast).{0,80}(\d{3})",
    }
    for key, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        data[key] = int(m.group(1)) if m else None

    # Capture everything from the "past 24 hours" sentence to the blank line
    # that precedes the next-24h block (may be multiple sentences).
    m = re.search(
        r"Space weather for the past 24 hours has been (.+?)(?=\n\n|\Z)",
        text, re.IGNORECASE | re.DOTALL
    )
    data["past_24h"] = " ".join(m.group(1).split()) if m else None

    # Next-24h phrasing varies: "predicted to be X" or "No storms predicted…"
    m = re.search(
        r"(?:Space weather for the next 24 hours is predicted to be (.+?)"
        r"|No space weather storms are predicted for the next 24 hours\.?)",
        text, re.IGNORECASE | re.DOTALL
    )
    if m:
        data["next_24h"] = m.group(1).strip() if m.group(1) else "No storms predicted"
    else:
        data["next_24h"] = None

    return data


def fetch_kp_index() -> dict:
    """Return the latest planetary Kp reading."""
    records = _get_json("/json/planetary_k_index_1m.json")
    latest = records[-1] if records else {}
    return {
        "time_tag": latest.get("time_tag"),
        "estimated_kp": latest.get("estimated_kp"),
        "kp_index": latest.get("kp_index"),
    }


def fetch_solar_flux() -> dict:
    """Return the most recent F10.7 solar flux value and 90-day mean."""
    records = _get_json("/json/f107_cm_flux.json")
    latest = records[-1] if records else {}
    return {
        "time_tag": latest.get("time_tag"),
        "flux": latest.get("flux"),
        "ninety_day_mean": latest.get("ninety_day_mean"),
    }


def fetch_xray_flux() -> dict:
    """Return latest GOES X-ray flux in both bands."""
    records = _get_json("/json/goes/primary/xrays-6-hour.json")
    # Records alternate between two energy bands; grab the last of each.
    by_band: dict[str, dict] = {}
    for rec in records:
        by_band[rec.get("energy", "")] = rec
    return {band: {"flux": r.get("observed_flux"), "time_tag": r.get("time_tag")}
            for band, r in by_band.items()}


def fetch_solar_wind() -> dict:
    """Return latest real-time solar wind plasma data (ACE/DSCOVR)."""
    records = _get_json("/json/rtsw/rtsw_wind_1m.json")
    latest = records[-1] if records else {}
    return {
        "time_tag": latest.get("time_tag"),
        "proton_speed": latest.get("proton_speed"),
        "proton_density": latest.get("proton_density"),
        "proton_temperature": latest.get("proton_temperature"),
        "source": latest.get("source"),
    }


def fetch_imf() -> dict:
    """Return latest IMF data plus a Bz trend over the past 30 minutes."""
    records = _get_json("/json/rtsw/rtsw_mag_1m.json")
    latest = records[-1] if records else {}

    # Bz trend: compare mean of oldest 15 vs newest 15 of the last 30 records.
    recent = [
        r["bz_gsm"] for r in records[-30:]
        if r.get("bz_gsm") is not None
    ]
    bz_trend: str | None = None
    if len(recent) >= 20:
        old_mean = sum(recent[:15]) / 15
        new_mean = sum(recent[-15:]) / 15
        delta = new_mean - old_mean
        if abs(delta) >= 2.0:
            direction = "northward" if delta > 0 else "southward"
            bz_trend = f"trending {direction} ({delta:+.1f} nT over 30 min)"

    return {
        "time_tag": latest.get("time_tag"),
        "bt": latest.get("bt"),
        "bz_gsm": latest.get("bz_gsm"),
        "by_gsm": latest.get("by_gsm"),
        "bx_gsm": latest.get("bx_gsm"),
        "source": latest.get("source"),
        "bz_trend": bz_trend,
    }


def fetch_flare_probabilities() -> list[dict]:
    """Return 3-day flare class probabilities parsed from the 3-day forecast text."""
    text = _get_text("/text/3-day-forecast.txt")

    # Extract the issue date to derive the three forecast dates
    date_match = re.search(r":Issued:\s+(\d{4})\s+(\w+)\s+(\d+)", text)
    if not date_match:
        return []

    # Find radio blackout probability table.
    # Format: day-label row then "R1-R2  40%  40%  40%" row
    days_match = re.search(
        r"Radio Blackout Forecast for\s+.+?\n\n\s+([\w]+ \d+)\s+([\w]+ \d+)\s+([\w]+ \d+)\s*\n"
        r"R1[- ]R2\s+([\d]+)%\s+([\d]+)%\s+([\d]+)%",
        text
    )
    day_labels: list[str] = []
    r1_probs: list[str] = []
    if days_match:
        day_labels = [days_match.group(1), days_match.group(2), days_match.group(3)]
        r1_probs = [days_match.group(4), days_match.group(5), days_match.group(6)]

    # Also grab S-scale (solar radiation) probabilities
    s1_match = re.search(
        r"S1 or greater\s+([\d]+)%\s+([\d]+)%\s+([\d]+)%", text
    )
    s1_probs = [s1_match.group(1), s1_match.group(2), s1_match.group(3)] if s1_match else ["?", "?", "?"]

    results = []
    for i in range(3):
        label = day_labels[i] if i < len(day_labels) else f"Day {i+1}"
        results.append({
            "date": label,
            "r1_radio_blackout_pct": r1_probs[i] if i < len(r1_probs) else "?",
            "s1_radiation_storm_pct": s1_probs[i],
        })
    return results


def fetch_3day_forecast() -> str:
    """Return raw 3-day geomagnetic/Kp forecast text."""
    return _get_text("/text/3-day-forecast.txt")


def fetch_alerts() -> list[dict]:
    """Return any active NOAA space weather alerts/watches/warnings."""
    records = _get_json("/json/products/alerts.json")
    return [
        {
            "product_id": r.get("product_id"),
            "issue_datetime": r.get("issue_datetime"),
            "message": r.get("message", "")[:300],
        }
        for r in records
    ]


def fetch_27day_outlook() -> str:
    """Return raw 27-day F10.7 and Ap outlook text."""
    return _get_text("/text/27-day-outlook.txt")


def fetch_all() -> dict:
    """Fetch all NOAA data sets and return as a single dict."""
    fetched: dict = {}
    tasks = {
        "wwv": fetch_wwv,
        "kp_index": fetch_kp_index,
        "solar_flux": fetch_solar_flux,
        "xray_flux": fetch_xray_flux,
        "solar_wind": fetch_solar_wind,
        "imf": fetch_imf,
        "flare_probabilities": fetch_flare_probabilities,
        "forecast_3day": fetch_3day_forecast,
        "alerts": fetch_alerts,
        "outlook_27day": fetch_27day_outlook,
    }
    for name, fn in tasks.items():
        try:
            fetched[name] = fn()
        except Exception as exc:
            fetched[name] = {"error": str(exc)}
    fetched["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return fetched
