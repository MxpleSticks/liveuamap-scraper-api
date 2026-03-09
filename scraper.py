from __future__ import annotations

import argparse
import json

from app.scraper_service import scrape_incidents


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape incidents from a LiveUAMap page and print JSON."
    )
    parser.add_argument("url", help="Example: https://iran.liveuamap.com/")
    parser.add_argument(
        "--max-incidents",
        type=int,
        default=None,
        help="Limit the number of incidents returned.",
    )
    parser.add_argument(
        "--skip-detail-source",
        action="store_true",
        help="Do not open each detail page; source_link will be the incident page URL.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30).",
    )

    args = parser.parse_args()
    incidents = scrape_incidents(
        url=args.url,
        max_incidents=args.max_incidents,
        resolve_source_links=not args.skip_detail_source,
        timeout=args.timeout,
    )
    print(json.dumps(incidents, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
