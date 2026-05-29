"""Scrapes current space weather conditions from spaceweather.com."""

from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

URL = "https://spaceweather.com/"
TIMEOUT = 20
HEADERS = {"User-Agent": "solar-forecast-bot/1.0"}


def fetch_all() -> dict:
    try:
        r = requests.get(URL, timeout=TIMEOUT, headers=HEADERS)
        r.raise_for_status()
    except Exception as exc:
        return {"error": str(exc)}

    soup = BeautifulSoup(r.text, "lxml")
    data: dict = {"fetched_at": datetime.now(timezone.utc).isoformat()}

    # --- Solar wind / current conditions table ---
    # spaceweather.com embeds key–value pairs in small tables or <font> tags.
    # We search for known labels and grab the adjacent value text.
    full_text = soup.get_text(" ", strip=True)

    import re

    def _find(pattern: str) -> str | None:
        m = re.search(pattern, full_text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    data["solar_wind_speed"] = _find(r"Solar Wind Speed[:\s]+([0-9.]+\s*km/s)")
    data["solar_wind_density"] = _find(r"(?:density|proton density)[:\s]+([0-9.]+\s*p?/?cm)")
    data["sunspot_number"] = _find(r"Sunspot Number[:\s]+(\d+)")
    data["solar_flux"] = _find(r"10\.7-cm radio flux[:\s]+(\d+)")

    # Flare activity — look for lines like "X1.2 flare" or "M-class"
    flares = re.findall(r"\b([BCMX]\d+(?:\.\d+)?)\s+(?:solar\s+)?flare", full_text, re.IGNORECASE)
    data["recent_flares"] = list(dict.fromkeys(flares))  # deduplicated, order preserved

    # NOAA forecast probabilities block (often present as a table)
    m_prob = _find(r"M-class\s*[\(\[]\s*(\d+)%")
    x_prob = _find(r"X-class\s*[\(\[]\s*(\d+)%")
    data["m_class_probability"] = m_prob
    data["x_class_probability"] = x_prob

    # Kp index
    data["kp_index"] = _find(r"Planetary K-index[:\s]+(\d+(?:\.\d+)?)")

    # Headline / top story text (first <h2> or bold paragraph)
    headline_tag = soup.find("h2") or soup.find("b")
    data["headline"] = headline_tag.get_text(strip=True)[:200] if headline_tag else None

    return data
