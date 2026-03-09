from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split())


def _build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _unix_to_iso_utc(unix_ts: Any) -> str | None:
    ts = _safe_int(unix_ts)
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _source_name_from_link(source_link: str) -> str:
    if not source_link:
        return ""

    parsed = urlparse(source_link)
    host = (parsed.netloc or "").lower().removeprefix("www.")
    path_parts = [part for part in parsed.path.split("/") if part]

    if host in {"x.com", "twitter.com"} and path_parts:
        return path_parts[0]

    if host in {"t.me", "telegram.me"} and path_parts:
        return path_parts[0]

    return host


def _normalize_relative_time(value: str | None) -> str:
    text = _clean_text(value)
    match = re.match(r"^(\d+)\s+([a-zA-Z]+)\s+ago$", text)
    if not match:
        return text

    amount = int(match.group(1))
    unit = match.group(2).lower()
    if amount == 1:
        unit = unit[:-1] if unit.endswith("s") else unit
    elif not unit.endswith("s"):
        unit = f"{unit}s"

    return f"{amount} {unit} ago"


def _extract_event_metadata(page_html: str) -> dict[str, dict[str, Any]]:
    """
    Extract metadata keyed by event id from the embedded LiveUAMap `ovens` payload.
    """
    match = re.search(r"var\s+ovens\s*=\s*'([^']+)'", page_html)
    if not match:
        return {}

    try:
        decoded = base64.b64decode(match.group(1)).decode("utf-8", errors="ignore")
        payload = json.loads(decoded)
    except (ValueError, json.JSONDecodeError):
        return {}

    metadata: dict[str, dict[str, Any]] = {}
    for venue in payload.get("venues", []):
        event_id = _clean_text(str(venue.get("id", "")))
        if not event_id:
            continue

        lat = _safe_float(venue.get("lat"))
        lng = _safe_float(venue.get("lng"))
        coordinates = (
            {"lat": lat, "lng": lng}
            if lat is not None and lng is not None
            else None
        )

        source_link = _clean_text(venue.get("source"))
        timestamp_utc = _unix_to_iso_utc(venue.get("timestamp"))
        relative_time = _normalize_relative_time(venue.get("time"))
        fallback_name = _clean_text(venue.get("name"))
        metadata[event_id] = {
            "coordinates": coordinates,
            "source_link": source_link,
            "timestamp_utc": timestamp_utc,
            "relative_time": relative_time,
            "name": fallback_name,
        }

    return metadata


@lru_cache(maxsize=2048)
def _source_link_from_detail(detail_url: str, timeout: int = 30) -> str:
    session = _build_session()
    response = session.get(detail_url, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    source_anchor = soup.select_one(".popup-box a.source-link[href]")

    if not source_anchor:
        return detail_url

    href = _clean_text(source_anchor.get("href"))
    if not href or href in {"/", "#"}:
        return detail_url

    return urljoin(detail_url, href)


def scrape_incidents(
    url: str,
    max_incidents: int | None = None,
    resolve_source_links: bool = True,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """
    Scrape incident data from a LiveUAMap page.

    Returns records in this shape:
    {
      "description": str,
      "source_link": str,
      "source_name": str,
      "date": str,
      "timestamp_utc": str | None,
      "location": str,
      "coordinates": {"lat": float, "lng": float} | None
    }
    """
    session = _build_session()
    response = session.get(url, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    incident_nodes = soup.select("div.event[data-link]")
    event_metadata = _extract_event_metadata(response.text)

    incidents: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for node in incident_nodes:
        event_id = _clean_text(node.get("data-id"))
        if event_id and event_id in seen_ids:
            continue
        if event_id:
            seen_ids.add(event_id)

        title_node = node.select_one(".title")
        date_node = node.select_one(".date_add")
        location_node = node.select_one("a.comment-link")

        description = _clean_text(title_node.get_text(" ", strip=True) if title_node else "")
        date = _normalize_relative_time(
            date_node.get_text(" ", strip=True) if date_node else ""
        )
        location = _clean_text(
            location_node.get_text(" ", strip=True) if location_node else ""
        )
        metadata = event_metadata.get(event_id, {})
        coordinates = metadata.get("coordinates")
        timestamp_utc = metadata.get("timestamp_utc")

        if not description:
            description = _clean_text(metadata.get("name"))
        if not date:
            date = _normalize_relative_time(metadata.get("relative_time"))

        detail_url = urljoin(url, _clean_text(node.get("data-link")))

        source_link_from_payload = _clean_text(metadata.get("source_link"))
        if source_link_from_payload:
            source_link = source_link_from_payload
        elif resolve_source_links:
            try:
                source_link = _source_link_from_detail(detail_url, timeout=timeout)
            except requests.RequestException:
                source_link = detail_url
        else:
            source_link = detail_url

        source_name = _source_name_from_link(source_link)

        incidents.append(
            {
                "description": description,
                "source_link": source_link,
                "source_name": source_name,
                "date": date,
                "timestamp_utc": timestamp_utc,
                "location": location,
                "coordinates": coordinates,
            }
        )

        if max_incidents is not None and len(incidents) >= max_incidents:
            break

    return incidents
