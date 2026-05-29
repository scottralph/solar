"""Scrapes DST index and Kp forecast range from spaceweatherlive.com."""

import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

URL = "https://www.spaceweatherlive.com/en/solar-activity.html"
TIMEOUT = 20
HEADERS = {"User-Agent": "solar-forecast-bot/1.0"}


def fetch_all() -> dict:
    try:
        r = requests.get(URL, timeout=TIMEOUT, headers=HEADERS)
        r.raise_for_status()
    except Exception as exc:
        return {"error": str(exc)}

    soup = BeautifulSoup(r.text, "lxml")
    full_text = soup.get_text(" ", strip=True)
    data: dict = {"fetched_at": datetime.now(timezone.utc).isoformat()}

    def _find(pattern: str) -> str | None:
        m = re.search(pattern, full_text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    # DST index (disturbance storm time — negative = geomagnetic storm)
    data["dst_index"] = _find(r"DST[:\s]+(-?\d+)\s*nT")

    # Kp forecast range — site shows e.g. "Kp2- to Kp4"
    kp_range = re.findall(r"Kp(\d[-+]?)", full_text)
    data["kp_forecast_range"] = kp_range[:6] if kp_range else None

    # Sunspot number and delta
    data["sunspot_number"] = _find(r"Sunspot number[:\s]+(\d+)")

    # Solar flux
    data["solar_flux"] = _find(r"F10\.7[:\s]+(\d+)")

    # Hemispheric power (proxy for auroral activity)
    data["hemispheric_power_gw"] = _find(r"Hemispheric power[:\s]+(\d+)\s*GW")

    # Flare probabilities
    data["c_class_probability"] = _find(r"C-class[:\s]+(\d+)%")
    data["m_class_probability"] = _find(r"M-class[:\s]+(\d+)%")
    data["x_class_probability"] = _find(r"X-class[:\s]+(\d+)%")

    # Current X-ray flux level label (e.g. "B2.3", "C1.1")
    data["xray_flux_level"] = _find(r"X-ray flux[:\s]+([ABCMX]\d+(?:\.\d+)?)")

    return data
