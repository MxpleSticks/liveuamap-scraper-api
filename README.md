# liveuamap-scraper-api

> Please support the original project at [LiveUAMap](https://liveuamap.com/) and use this viewer responsibly with attribution.

## Important Disclaimer

- This project runs on the **Render free tier**, so it can be slow and may have cold starts.
- This is **not a database** and **not the official LiveUAMap API**.
- It is a **remote scraper** that fetches incident data from public LiveUAMap pages on demand.
- Typical request time is about **2-4 seconds** when requesting **30 incidents** (the current limit), so performance is okay for testing but not instant.
- This is meant for **hobby/testing use**, not serious professional or mission-critical production use.
- If you need a faster, easier, and more reliable API, buy the official one:
  - [LiveUAMap API pricing / signup](https://liveuamap.com/promo/api)

FastAPI service that scrapes global incident updates from LiveUAMap region and topic pages.

## Use This API (Hobby / Testing)

Base URL:

- `https://liveuamap-scraper-api-v6jt.onrender.com`

Most-used endpoints:

- `GET /health`
- `GET /conflicts`
- `GET /scrape?conflict=<preset>&max_incidents=<n>`
- `GET /scrape?url=<full_liveuamap_url>&max_incidents=<n>`

Example calls:

```powershell
curl "https://liveuamap-scraper-api-v6jt.onrender.com/health"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/conflicts"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=ukraine&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?url=https://taiwan.liveuamap.com/&max_incidents=20"
```

## What It Returns

Each incident includes:

- `description`
- `source_link`
- `source_name`
- `date` (relative text like `2 hours ago`)
- `timestamp_utc` (absolute ISO UTC like `2026-03-08T19:31:00Z`)
- `location`
- `coordinates` (`{"lat": ..., "lng": ...}` or `null`)

Current response restriction:

- Most recent `30` incidents per request.

## Safety Features

- Per-IP rate limiting (default: `90` requests per `60` seconds)
- URL host allowlist (default: `iran.liveuamap.com,*.liveuamap.com`)
- Max incident cap (default: `100`)
- Short in-memory response cache (default: `90` seconds)

## Local Run (Optional)

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open docs:

- [http://localhost:8000/docs](http://localhost:8000/docs)

Example call:

```powershell
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=taiwan&max_incidents=20"
```

## Pick A Conflict

You can choose a conflict in two ways.

1. Recommended: use the `conflict` parameter (preset targets).
2. Advanced: pass a direct `url`.
3. Pass only one of `conflict` or `url` per request.

Supported preset values:

- `iran` -> `https://iran.liveuamap.com/`
- `ukraine` -> `https://ukraine.liveuamap.com/`
- `taiwan` -> `https://taiwan.liveuamap.com/`
- `japan` -> `https://japan.liveuamap.com/`
- `vietnam` -> `https://vietnam.liveuamap.com/`
- `thailand` -> `https://thailand.liveuamap.com/`
- `bangladesh` -> `https://bangladesh.liveuamap.com/`
- `indonesia` -> `https://indonesia.liveuamap.com/`
- `koreas` -> `https://koreas.liveuamap.com/`
- `hongkong` -> `https://hongkong.liveuamap.com/`
- `china` -> `https://china.liveuamap.com/`
- `myanmar` -> `https://myanmar.liveuamap.com/`
- `india` -> `https://india.liveuamap.com/`
- `kashmir` -> `https://kashmir.liveuamap.com/`
- `philippines` -> `https://philippines.liveuamap.com/`
- `srilanka` -> `https://srilanka.liveuamap.com/`
- `maldives` -> `https://maldives.liveuamap.com/`
- `syria` -> `https://syria.liveuamap.com/`
- `yemen` -> `https://yemen.liveuamap.com/`
- `israelpalestine` -> `https://israelpalestine.liveuamap.com/`
- `turkey` -> `https://turkey.liveuamap.com/`
- `egypt` -> `https://egypt.liveuamap.com/`
- `iraq` -> `https://iraq.liveuamap.com/`
- `libya` -> `https://libya.liveuamap.com/`
- `centralasia` -> `https://centralasia.liveuamap.com/`
- `kurds` -> `https://kurds.liveuamap.com/`
- `afghanistan` -> `https://afghanistan.liveuamap.com/`
- `qatar` -> `https://qatar.liveuamap.com/`
- `pakistan` -> `https://pakistan.liveuamap.com/`
- `hezbollah` -> `https://hezbollah.liveuamap.com/`
- `lebanon` -> `https://lebanon.liveuamap.com/`
- `tunisia` -> `https://tunisia.liveuamap.com/`
- `algeria` -> `https://algeria.liveuamap.com/`
- `saudiarabia` -> `https://saudiarabia.liveuamap.com/`
- `russia` -> `https://russia.liveuamap.com/`
- `hungary` -> `https://hungary.liveuamap.com/`
- `ireland` -> `https://ireland.liveuamap.com/`
- `caucasus` -> `https://caucasus.liveuamap.com/`
- `balkans` -> `https://balkans.liveuamap.com/`
- `poland` -> `https://poland.liveuamap.com/`
- `belarus` -> `https://belarus.liveuamap.com/`
- `baltics` -> `https://baltics.liveuamap.com/`
- `spain` -> `https://spain.liveuamap.com/`
- `germany` -> `https://germany.liveuamap.com/`
- `france` -> `https://france.liveuamap.com/`
- `uk` -> `https://uk.liveuamap.com/`
- `moldova` -> `https://moldova.liveuamap.com/`
- `italy` -> `https://italy.liveuamap.com/`
- `cameroon` -> `https://cameroon.liveuamap.com/`
- `tanzania` -> `https://tanzania.liveuamap.com/`
- `nigeria` -> `https://nigeria.liveuamap.com/`
- `ethiopia` -> `https://ethiopia.liveuamap.com/`
- `somalia` -> `https://somalia.liveuamap.com/`
- `kenya` -> `https://kenya.liveuamap.com/`
- `alshabab` -> `https://alshabab.liveuamap.com/`
- `uganda` -> `https://uganda.liveuamap.com/`
- `sudan` -> `https://sudan.liveuamap.com/`
- `drcongo` -> `https://drcongo.liveuamap.com/`
- `southafrica` -> `https://southafrica.liveuamap.com/`
- `sahel` -> `https://sahel.liveuamap.com/`
- `centralafrica` -> `https://centralafrica.liveuamap.com/`
- `zimbabwe` -> `https://zimbabwe.liveuamap.com/`
- `colombia` -> `https://colombia.liveuamap.com/`
- `brazil` -> `https://brazil.liveuamap.com/`
- `venezuela` -> `https://venezuela.liveuamap.com/`
- `mexico` -> `https://mexico.liveuamap.com/`
- `caribbean` -> `https://caribbean.liveuamap.com/`
- `guyana` -> `https://guyana.liveuamap.com/`
- `puertorico` -> `https://puertorico.liveuamap.com/`
- `nicaragua` -> `https://nicaragua.liveuamap.com/`
- `latam` -> `https://latam.liveuamap.com/`
- `canada` -> `https://canada.liveuamap.com/`
- `honduras` -> `https://honduras.liveuamap.com/`
- `argentina` -> `https://argentina.liveuamap.com/`
- `bolivia` -> `https://bolivia.liveuamap.com/`
- `chile` -> `https://chile.liveuamap.com/`
- `peru` -> `https://peru.liveuamap.com/`
- `usa` -> `https://usa.liveuamap.com/`
- `isis` -> `https://isis.liveuamap.com/`
- `health` -> `https://health.liveuamap.com/`

Examples:

```powershell
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=ukraine&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=iran&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=taiwan&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=india&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=syria&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=israelpalestine&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=russia&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=uk&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=nigeria&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=drcongo&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=mexico&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=usa&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=isis&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=health&max_incidents=20"
curl "https://liveuamap-scraper-api-v6jt.onrender.com/scrape?url=https://ukraine.liveuamap.com/&max_incidents=20"
```

Note:

- `ukraine` map already includes Russia-related incidents in the feed.
- `iran` map includes related events from nearby actors/regions where relevant.

## Live API URLs

Base URL:

- `https://liveuamap-scraper-api-v6jt.onrender.com`

Direct endpoints:

- `https://liveuamap-scraper-api-v6jt.onrender.com/health`
- `https://liveuamap-scraper-api-v6jt.onrender.com/conflicts`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=iran&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=ukraine&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=taiwan&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=india&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=syria&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=russia&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=nigeria&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=usa&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=isis&max_incidents=20`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?conflict=ukraine&max_incidents=20&skip_detail_source=true`
- `https://liveuamap-scraper-api-v6jt.onrender.com/scrape?url=https://iran.liveuamap.com/&max_incidents=20`

Get available presets:

```powershell
curl "https://liveuamap-scraper-api-v6jt.onrender.com/conflicts"
```

## Keep CLI Script

You can still run the direct script mode:

```powershell
python scraper.py https://iran.liveuamap.com/ --max-incidents 20
```
