"""Scrapes data and reports from spaceweatherlive.com."""

import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

BASE = "https://www.spaceweatherlive.com"
TIMEOUT = 20
HEADERS = {"User-Agent": "solar-forecast-bot/1.0"}


def _get_soup(path: str) -> BeautifulSoup:
    r = requests.get(f"{BASE}{path}", timeout=TIMEOUT, headers=HEADERS)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")


def _strip_boilerplate(soup: BeautifulSoup) -> str:
    """Remove nav/footer/scripts and return clean text."""
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)


def fetch_dashboard() -> dict:
    """Scrape real-time indices from the solar activity dashboard."""
    soup = _get_soup("/en/solar-activity.html")
    full_text = soup.get_text(" ", strip=True)
    data: dict = {}

    def _find(pattern: str) -> str | None:
        m = re.search(pattern, full_text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    data["dst_index"] = _find(r"DST[:\s]+(-?\d+)\s*nT")
    data["sunspot_number"] = _find(r"Sunspot number[:\s]+(\d+)")
    data["solar_flux"] = _find(r"F10\.7[:\s]+(\d+)")
    data["hemispheric_power_gw"] = _find(r"Hemispheric power[:\s]+(\d+)\s*GW")
    data["c_class_probability"] = _find(r"C-class[:\s]+(\d+)%")
    data["m_class_probability"] = _find(r"M-class[:\s]+(\d+)%")
    data["x_class_probability"] = _find(r"X-class[:\s]+(\d+)%")
    data["xray_flux_level"] = _find(r"X-ray flux[:\s]+([ABCMX]\d+(?:\.\d+)?)")

    kp_range = re.findall(r"Kp(\d[-+]?)", full_text)
    data["kp_forecast_range"] = kp_range[:6] if kp_range else None

    return data


_STOP_MARKERS = (
    "Back to top",
    "A lot of people come to SpaceWeatherLive",
    "Latest news",
    "Support SpaceWeatherLive",
)


def _is_heading(line: str) -> bool:
    """True if line looks like a section heading rather than prose."""
    # Headings are short, capitalised, and don't end in sentence punctuation.
    return len(line) <= 30 and not line[-1] in ".,:;)" and line[0].isupper()


def _extract_body(text: str, start_marker: str) -> str:
    """Return text between start_marker and the first boilerplate stop marker.

    Section headings become paragraph breaks prefixed with '### '.
    Consecutive prose lines are joined; blank lines are paragraph separators.
    The result uses '\\n\\n' as the paragraph separator throughout.
    """
    lines = text.splitlines()
    capturing = False
    segments: list[str] = []   # alternating headings and prose chunks
    current: list[str] = []    # lines accumulating in current prose paragraph

    def flush() -> None:
        if current:
            segments.append(" ".join(current))
            current.clear()

    for line in lines:
        stripped = line.strip()

        if not capturing:
            if start_marker in stripped:
                capturing = True
            continue

        if any(m in stripped for m in _STOP_MARKERS):
            break

        if not stripped:
            flush()
            continue

        if _is_heading(stripped):
            flush()
            segments.append(f"### {stripped}")
        else:
            current.append(stripped)

    flush()
    return "\n\n".join(s for s in segments if s).strip()


def fetch_forecast_discussion() -> dict:
    """Fetch the NOAA forecast discussion narrative (issued daily)."""
    soup = _get_soup("/en/reports/forecast-discussion.html")
    text = _strip_boilerplate(soup)
    body = _extract_body(text, "Space Weather Prediction Center")

    issue_match = re.search(r"(\d{4} \w+ \d{1,2} \d{4} UTC)", body)
    issue_time = issue_match.group(1) if issue_match else None

    return {"issue_time": issue_time, "text": body}


def fetch_solar_activity_report() -> dict:
    """Fetch the daily NOAA solar & geomagnetic activity report."""
    soup = _get_soup("/en/reports/solar-activity-report.html")
    text = _strip_boilerplate(soup)
    body = _extract_body(text, "Joint USAF/NOAA Report")
    return {"text": body}


def fetch_all() -> dict:
    data: dict = {"fetched_at": datetime.now(timezone.utc).isoformat()}
    for name, fn in [
        ("dashboard", fetch_dashboard),
        ("forecast_discussion", fetch_forecast_discussion),
    ]:
        try:
            data[name] = fn()
        except Exception as exc:
            data[name] = {"error": str(exc)}
    return data
