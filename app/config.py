from __future__ import annotations

import os
from dataclasses import dataclass


def _get_int(name: str, default: int, minimum: int, maximum: int | None = None) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError:
        value = default

    if value < minimum:
        value = minimum
    if maximum is not None and value > maximum:
        value = maximum
    return value


def _get_allowed_hosts() -> tuple[str, ...]:
    raw = os.getenv("ALLOWED_HOSTS", "iran.liveuamap.com,*.liveuamap.com")
    hosts = tuple(part.strip().lower() for part in raw.split(",") if part.strip())
    return hosts or ("iran.liveuamap.com", "*.liveuamap.com")


@dataclass(frozen=True)
class Settings:
    rate_limit_requests: int
    rate_limit_window_seconds: int
    max_incidents_cap: int
    cache_ttl_seconds: int
    request_timeout_seconds: int
    allowed_hosts: tuple[str, ...]


def load_settings() -> Settings:
    return Settings(
        rate_limit_requests=_get_int("RATE_LIMIT_REQUESTS", 90, minimum=1, maximum=600),
        rate_limit_window_seconds=_get_int(
            "RATE_LIMIT_WINDOW_SECONDS", 60, minimum=1, maximum=3600
        ),
        max_incidents_cap=_get_int("MAX_INCIDENTS_CAP", 100, minimum=1, maximum=500),
        cache_ttl_seconds=_get_int("CACHE_TTL_SECONDS", 90, minimum=1, maximum=3600),
        request_timeout_seconds=_get_int(
            "REQUEST_TIMEOUT_SECONDS", 30, minimum=5, maximum=120
        ),
        allowed_hosts=_get_allowed_hosts(),
    )


SETTINGS = load_settings()
