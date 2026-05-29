"""Aggregates fetched space weather data into a radio condition forecast report."""

from __future__ import annotations

import re
import textwrap
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Propagation condition helpers
# ---------------------------------------------------------------------------

def _sfi_label(sfi: int | None) -> str:
    if sfi is None:
        return "unknown"
    if sfi >= 150:
        return "excellent"
    if sfi >= 120:
        return "good"
    if sfi >= 90:
        return "fair"
    return "poor"


def _kp_label(kp: float | None) -> str:
    if kp is None:
        return "unknown"
    if kp <= 2:
        return "quiet"
    if kp <= 3:
        return "unsettled"
    if kp <= 4:
        return "active"
    if kp <= 5:
        return "minor storm (G1)"
    if kp <= 6:
        return "moderate storm (G2)"
    return "severe storm (G3+)"


def _xray_label(flux: float | None) -> str:
    """Classify X-ray flux level from W/m² value."""
    if flux is None:
        return "unknown"
    if flux < 1e-7:
        return "A-class (very low)"
    if flux < 1e-6:
        return "B-class (low)"
    if flux < 1e-5:
        return "C-class (moderate)"
    if flux < 1e-4:
        return "M-class (high)"
    return "X-class (very high)"


def _dst_label(dst: str | None) -> str:
    if dst is None:
        return "unknown"
    try:
        v = int(dst)
    except ValueError:
        return dst
    if v > -20:
        return f"{v} nT (quiet)"
    if v > -50:
        return f"{v} nT (minor disturbance)"
    if v > -100:
        return f"{v} nT (moderate storm)"
    return f"{v} nT (intense storm)"


def _extract_kp_forecast_from_3day(text: str) -> list[str]:
    """Pull the Kp breakdown table from the NOAA 3-day forecast text."""
    lines = []
    capture = False
    for line in text.splitlines():
        if re.search(r"kp index breakdown", line, re.IGNORECASE):
            capture = True
        if capture:
            lines.append(line)
        if capture and len(lines) > 14:
            break
    return lines


# ---------------------------------------------------------------------------
# Main report builder
# ---------------------------------------------------------------------------

def build(noaa: dict, swcom: dict, swlive: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    lines: list[str] = []

    def section(title: str) -> None:
        lines.append("")
        lines.append(f"{'=' * 60}")
        lines.append(f"  {title}")
        lines.append(f"{'=' * 60}")

    def row(label: str, value: str) -> None:
        lines.append(f"  {label:<30} {value}")

    lines.append(f"RADIO CONDITION FORECAST — generated {now}")
    lines.append("Sources: NOAA SWPC · spaceweather.com · spaceweatherlive.com")

    # ── Current Conditions ──────────────────────────────────────────────────
    section("CURRENT CONDITIONS")

    wwv = noaa.get("wwv", {})
    sf = noaa.get("solar_flux", {})
    kp = noaa.get("kp_index", {})
    wind = noaa.get("solar_wind", {})
    xray = noaa.get("xray_flux", {})
    swl = swlive

    sfi_val = sf.get("flux") or wwv.get("solar_flux")
    sfi_mean = sf.get("ninety_day_mean")
    kp_val = kp.get("estimated_kp")
    kp_int = kp.get("kp_index")

    row("F10.7 Solar Flux (SFI):",
        f"{sfi_val} sfu  [{_sfi_label(sfi_val)}]" if sfi_val else "n/a")
    if sfi_mean:
        row("  90-day mean:", f"{sfi_mean} sfu")
    row("Planetary Kp Index:",
        f"{kp_val}  [{_kp_label(kp_val)}]" if kp_val is not None else "n/a")
    row("  NOAA A-index:", f"{wwv.get('a_index', 'n/a')}")

    # X-ray flux
    long_band = xray.get("0.1-0.8nm") or xray.get("0.1-0.8 nm", {})
    xflux = long_band.get("flux") if isinstance(long_band, dict) else None
    row("X-ray flux (0.1–0.8 nm):", _xray_label(xflux))

    # Solar wind
    spd = wind.get("proton_speed")
    den = wind.get("proton_density")
    src = wind.get("source", "")
    row("Solar wind speed:", f"{spd} km/s  [{src}]" if spd else "n/a")
    row("Solar wind density:", f"{den} p/cm³" if den else "n/a")

    # DST
    row("DST index:", _dst_label(swl.get("dst_index")))

    # ── Propagation Summary ─────────────────────────────────────────────────
    section("PROPAGATION SUMMARY")

    sfi_n = int(sfi_val) if sfi_val else None
    kp_n = float(kp_val) if kp_val is not None else None

    if sfi_n and sfi_n >= 120:
        hf_note = "HF conditions favourable — elevated solar flux supports higher MUF."
    elif sfi_n and sfi_n >= 90:
        hf_note = "HF conditions moderate — typical MUF, seasonal paths likely."
    elif sfi_n:
        hf_note = "HF conditions marginal — low solar flux limits higher bands."
    else:
        hf_note = "HF conditions unknown (SFI unavailable)."

    if kp_n is not None and kp_n >= 5:
        geo_note = f"Geomagnetic storm (Kp {kp_n}) — expect absorption and polar path degradation."
    elif kp_n is not None and kp_n >= 4:
        geo_note = "Active geomagnetic conditions — higher-latitude paths may be affected."
    elif kp_n is not None:
        geo_note = "Geomagnetic conditions quiet to unsettled — no significant path disruption expected."
    else:
        geo_note = "Geomagnetic conditions unknown."

    for line in textwrap.wrap(hf_note, 58):
        lines.append(f"  {line}")
    lines.append("")
    for line in textwrap.wrap(geo_note, 58):
        lines.append(f"  {line}")

    past = wwv.get("past_24h")
    nxt = wwv.get("next_24h")
    if past:
        lines.append("")
        lines.append(f"  Past 24h:  {past}")
    if nxt:
        lines.append(f"  Next 24h:  {nxt}")

    # ── 3-Day Event Probabilities ───────────────────────────────────────────
    section("3-DAY EVENT PROBABILITIES  (from NOAA 3-day forecast)")
    probs = noaa.get("flare_probabilities", [])
    if probs and not isinstance(probs, dict):
        lines.append(f"  {'Day':<12} {'R1 Blackout%':>14} {'S1 Radiation%':>15}")
        lines.append(f"  {'-'*44}")
        for p in probs:
            date = (p.get("date") or "")[:12]
            lines.append(
                f"  {date:<12} {str(p.get('r1_radio_blackout_pct','?')):>14} "
                f"{str(p.get('s1_radiation_storm_pct','?')):>15}"
            )
    else:
        lines.append("  (unavailable)")

    # ── Kp Forecast (3-day) ─────────────────────────────────────────────────
    section("Kp FORECAST (3-DAY)")
    forecast_text = noaa.get("forecast_3day", "")
    if isinstance(forecast_text, str) and forecast_text:
        kp_lines = _extract_kp_forecast_from_3day(forecast_text)
        for fl in kp_lines[:12]:
            if fl.strip():
                lines.append(f"  {fl}")
    else:
        lines.append("  (unavailable)")

    # Spaceweatherlive Kp range
    kp_range = swl.get("kp_forecast_range")
    if kp_range:
        lines.append(f"\n  SWLive Kp range seen: {', '.join(kp_range)}")

    # ── Active Alerts ───────────────────────────────────────────────────────
    alerts = noaa.get("alerts", [])
    if alerts and not isinstance(alerts, dict):
        section("ACTIVE NOAA ALERTS / WARNINGS")
        for a in alerts[:5]:
            pid = a.get("product_id", "")
            issued = (a.get("issue_datetime") or "")[:16]
            lines.append(f"  [{pid}]  {issued}")
            msg_first = (a.get("message") or "").split("\n")[0][:70]
            if msg_first:
                lines.append(f"    {msg_first}")

    # ── News Headline ───────────────────────────────────────────────────────
    headline = swcom.get("headline")
    if headline and "error" not in swcom:
        section("SPACEWEATHER.COM HEADLINE")
        for line in textwrap.wrap(headline, 58):
            lines.append(f"  {line}")

    # ── Footer ──────────────────────────────────────────────────────────────
    lines.append("")
    lines.append("=" * 60)
    lines.append("  All times UTC.  Data sourced from public feeds.")
    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)
