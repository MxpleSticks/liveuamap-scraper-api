from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.cache import TTLCache
from app.config import SETTINGS
from app.rate_limiter import InMemoryRateLimiter
from app.scraper_service import scrape_incidents


app = FastAPI(
    title="liveuamap-scraper-api",
    description="Global incident feed scraper for LiveUAMap region and topic pages.",
    version="1.0.0",
)

# Public API: allow cross-origin reads from browser clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

rate_limiter = InMemoryRateLimiter(
    max_requests=SETTINGS.rate_limit_requests,
    window_seconds=SETTINGS.rate_limit_window_seconds,
)
response_cache = TTLCache(ttl_seconds=SETTINGS.cache_ttl_seconds, max_entries=256)
SITE_FILE = Path(__file__).resolve().parent / "static" / "index.html"

CONFLICT_URLS = {
    "iran": "https://iran.liveuamap.com/",
    "ukraine": "https://ukraine.liveuamap.com/",
    "taiwan": "https://taiwan.liveuamap.com/",
    "japan": "https://japan.liveuamap.com/",
    "vietnam": "https://vietnam.liveuamap.com/",
    "thailand": "https://thailand.liveuamap.com/",
    "bangladesh": "https://bangladesh.liveuamap.com/",
    "indonesia": "https://indonesia.liveuamap.com/",
    "koreas": "https://koreas.liveuamap.com/",
    "hongkong": "https://hongkong.liveuamap.com/",
    "china": "https://china.liveuamap.com/",
    "myanmar": "https://myanmar.liveuamap.com/",
    "india": "https://india.liveuamap.com/",
    "kashmir": "https://kashmir.liveuamap.com/",
    "philippines": "https://philippines.liveuamap.com/",
    "srilanka": "https://srilanka.liveuamap.com/",
    "maldives": "https://maldives.liveuamap.com/",
    "syria": "https://syria.liveuamap.com/",
    "yemen": "https://yemen.liveuamap.com/",
    "israelpalestine": "https://israelpalestine.liveuamap.com/",
    "turkey": "https://turkey.liveuamap.com/",
    "egypt": "https://egypt.liveuamap.com/",
    "iraq": "https://iraq.liveuamap.com/",
    "libya": "https://libya.liveuamap.com/",
    "centralasia": "https://centralasia.liveuamap.com/",
    "kurds": "https://kurds.liveuamap.com/",
    "afghanistan": "https://afghanistan.liveuamap.com/",
    "qatar": "https://qatar.liveuamap.com/",
    "pakistan": "https://pakistan.liveuamap.com/",
    "hezbollah": "https://hezbollah.liveuamap.com/",
    "lebanon": "https://lebanon.liveuamap.com/",
    "tunisia": "https://tunisia.liveuamap.com/",
    "algeria": "https://algeria.liveuamap.com/",
    "saudiarabia": "https://saudiarabia.liveuamap.com/",
    "russia": "https://russia.liveuamap.com/",
    "hungary": "https://hungary.liveuamap.com/",
    "ireland": "https://ireland.liveuamap.com/",
    "caucasus": "https://caucasus.liveuamap.com/",
    "balkans": "https://balkans.liveuamap.com/",
    "poland": "https://poland.liveuamap.com/",
    "belarus": "https://belarus.liveuamap.com/",
    "baltics": "https://baltics.liveuamap.com/",
    "spain": "https://spain.liveuamap.com/",
    "germany": "https://germany.liveuamap.com/",
    "france": "https://france.liveuamap.com/",
    "uk": "https://uk.liveuamap.com/",
    "moldova": "https://moldova.liveuamap.com/",
    "italy": "https://italy.liveuamap.com/",
    "cameroon": "https://cameroon.liveuamap.com/",
    "tanzania": "https://tanzania.liveuamap.com/",
    "nigeria": "https://nigeria.liveuamap.com/",
    "ethiopia": "https://ethiopia.liveuamap.com/",
    "somalia": "https://somalia.liveuamap.com/",
    "kenya": "https://kenya.liveuamap.com/",
    "alshabab": "https://alshabab.liveuamap.com/",
    "uganda": "https://uganda.liveuamap.com/",
    "sudan": "https://sudan.liveuamap.com/",
    "drcongo": "https://drcongo.liveuamap.com/",
    "southafrica": "https://southafrica.liveuamap.com/",
    "sahel": "https://sahel.liveuamap.com/",
    "centralafrica": "https://centralafrica.liveuamap.com/",
    "zimbabwe": "https://zimbabwe.liveuamap.com/",
    "colombia": "https://colombia.liveuamap.com/",
    "brazil": "https://brazil.liveuamap.com/",
    "venezuela": "https://venezuela.liveuamap.com/",
    "mexico": "https://mexico.liveuamap.com/",
    "caribbean": "https://caribbean.liveuamap.com/",
    "guyana": "https://guyana.liveuamap.com/",
    "puertorico": "https://puertorico.liveuamap.com/",
    "nicaragua": "https://nicaragua.liveuamap.com/",
    "latam": "https://latam.liveuamap.com/",
    "canada": "https://canada.liveuamap.com/",
    "honduras": "https://honduras.liveuamap.com/",
    "argentina": "https://argentina.liveuamap.com/",
    "bolivia": "https://bolivia.liveuamap.com/",
    "chile": "https://chile.liveuamap.com/",
    "peru": "https://peru.liveuamap.com/",
    "usa": "https://usa.liveuamap.com/",
    "isis": "https://isis.liveuamap.com/",
    "health": "https://health.liveuamap.com/",
}

CONFLICT_BY_HOST: dict[str, str] = {}
for conflict_name, preset_url in CONFLICT_URLS.items():
    host = (urlparse(preset_url).hostname or "").lower()
    if host:
        CONFLICT_BY_HOST[host] = conflict_name


def _host_allowed(host: str | None) -> bool:
    if not host:
        return False

    host = host.lower().strip(".")
    for pattern in SETTINGS.allowed_hosts:
        pattern = pattern.lower().strip()
        if not pattern:
            continue
        if pattern.startswith("*."):
            suffix = pattern[1:]  # ".example.com"
            if host.endswith(suffix):
                return True
        elif host == pattern:
            return True
    return False


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed.")
    if not _host_allowed(parsed.hostname):
        allowed = ", ".join(SETTINGS.allowed_hosts)
        raise HTTPException(
            status_code=400,
            detail=f"URL host is not allowed. Allowed hosts: {allowed}",
        )


def _resolve_target_url(
    conflict: str | None, url: str | None
) -> str:
    if conflict and url:
        raise HTTPException(
            status_code=400,
            detail="Use either conflict or url, not both.",
        )
    if conflict:
        normalized_conflict = conflict.strip().lower()
        if normalized_conflict in CONFLICT_URLS:
            return CONFLICT_URLS[normalized_conflict]
        available = ", ".join(CONFLICT_URLS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unknown conflict '{conflict}'. Available conflicts: {available}",
        )
    if url:
        cleaned_url = url.strip()
        if cleaned_url:
            return cleaned_url
    raise HTTPException(
        status_code=400,
        detail="Provide conflict or url.",
    )


def _infer_conflict(url: str) -> str | None:
    host = (urlparse(url).hostname or "").lower()
    return CONFLICT_BY_HOST.get(host)


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        first = forwarded.split(",")[0].strip()
        if first:
            return first

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "liveuamap-scraper-api",
        "status": "ok",
        "docs": "/docs",
        "conflicts": "/conflicts",
        "site": "/site",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/conflicts")
def conflicts() -> dict[str, dict[str, str]]:
    return {"available": CONFLICT_URLS}


@app.get("/site", include_in_schema=False)
def site() -> FileResponse:
    return FileResponse(SITE_FILE)


@app.get("/scrape")
def scrape(
    request: Request,
    response: Response,
    conflict: str | None = Query(
        None,
        description="Preset conflict target. See /conflicts for available values.",
    ),
    url: str | None = Query(
        None,
        description="Custom target URL, e.g. https://iran.liveuamap.com/. Use this OR conflict.",
    ),
    max_incidents: int = Query(
        50, ge=1, description="How many incidents to return (capped server-side)."
    ),
    skip_detail_source: bool = Query(
        False,
        description="If true, do not fetch each detail page when source link is missing.",
    ),
    timeout: int | None = Query(
        None,
        ge=5,
        le=120,
        description="Request timeout in seconds for upstream fetches.",
    ),
) -> dict:
    target_url = _resolve_target_url(conflict, url)
    _validate_url(target_url)

    limiter_result = rate_limiter.check(_client_key(request))
    response.headers["X-RateLimit-Limit"] = str(SETTINGS.rate_limit_requests)
    response.headers["X-RateLimit-Remaining"] = str(limiter_result.remaining)
    response.headers["X-RateLimit-Reset"] = str(limiter_result.reset_after_seconds)

    if not limiter_result.allowed:
        response.headers["Retry-After"] = str(limiter_result.retry_after_seconds)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry in {limiter_result.retry_after_seconds} seconds.",
        )

    safe_max = min(max_incidents, SETTINGS.max_incidents_cap)
    effective_timeout = timeout or SETTINGS.request_timeout_seconds
    cache_key = (target_url, safe_max, skip_detail_source, effective_timeout)

    cached = response_cache.get(cache_key)
    if cached is not None:
        return {
            "url": target_url,
            "conflict": _infer_conflict(target_url),
            "count": len(cached),
            "incidents": cached,
            "cached": True,
        }

    try:
        incidents = scrape_incidents(
            url=target_url,
            max_incidents=safe_max,
            resolve_source_links=not skip_detail_source,
            timeout=effective_timeout,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream fetch failed: {exc.__class__.__name__}",
        ) from exc

    response_cache.set(cache_key, incidents)
    return {
        "url": target_url,
        "conflict": _infer_conflict(target_url),
        "count": len(incidents),
        "incidents": incidents,
        "cached": False,
    }
