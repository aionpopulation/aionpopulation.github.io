#!/usr/bin/env python3
"""
Aion Private Server Population Scraper
Runs as a GitHub Actions cron job and writes data.json.
"""

import re
import json
import sys
from datetime import datetime, timezone

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def scrape_euroaion():
    """HTML SSR — <strong>ONLINE</strong> 303"""
    try:
        r = requests.get("https://euroaion.com/en-US", headers=HEADERS, timeout=15)
        r.raise_for_status()
        text = r.text
        players = None
        m = re.search(r"ONLINE</strong>\s*(\d+)", text)
        if m:
            players = int(m.group(1))
        return _ok("EuroAion", "https://euroaion.com/en-US", "4.6", players)
    except Exception as exc:
        return _err("EuroAion", "https://euroaion.com/en-US", "4.6", exc)


def scrape_aionempire():
    """HTML SSR — Онлайн <b>1353</b>  (or English variant)"""
    try:
        r = requests.get("https://aionempire.com/", headers=HEADERS, timeout=15)
        r.raise_for_status()
        text = r.text
        players = None
        m = re.search(r"[Оо]нлайн\s*<b>(\d+)</b>|Online\s*<b>(\d+)</b>", text)
        if m:
            players = int(m.group(1) or m.group(2))
        return _ok("AionEmpire", "https://aionempire.com", "2.0", players)
    except Exception as exc:
        return _err("AionEmpire", "https://aionempire.com", "2.0", exc)


def scrape_gamezaion():
    """HTML SSR — <span data-online>120</span> Online  (Cloudflare JS challenge blocks scrapers)"""
    NOTE = "Population unavailable — bot protection prevents scraping"
    try:
        try:
            from curl_cffi import requests as cf
            r = cf.get("https://gamezaion.com/", impersonate="chrome124", timeout=20)
        except ImportError:
            r = requests.get("https://gamezaion.com/", headers=HEADERS, timeout=15)
        r.raise_for_status()
        text = r.text
        players = None
        m = re.search(r'data-online>(\d+)<', text)
        if m:
            players = int(m.group(1))
        return _ok("GamezAion", "https://gamezaion.com", "4.8", players)
    except Exception:
        return _ok("GamezAion", "https://gamezaion.com", "4.8", None, online=None, note=NOTE, unavailable=True)


def scrape_originaion():
    """JSON API — GET /api/server-status"""
    try:
        r = requests.get(
            "https://originaion.com/api/server-status",
            headers=HEADERS, timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        is_online = data.get("isOnline", False)
        count = data.get("playerCount") or {}
        players = count.get("total")
        return _ok("OriginAion", "https://originaion.com", "4.6", players, online=is_online)
    except Exception as exc:
        return _err("OriginAion", "https://originaion.com", "4.6", exc)


def scrape_aionriftshade():
    """No public in-game player count API exists."""
    return _ok(
        "AionRiftShade", "https://aionriftshade.com", "4.8",
        players=None, online=None,
        note="No public player count available",
        unavailable=True,
    )


def scrape_aiondestiny():
    """JSON API — GET /api/online  →  {total, light (Elyos), dark (Asmo), serverStatus}"""
    try:
        r = requests.get(
            "https://aiondestiny.net/api/online",
            headers=HEADERS, timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        is_online = data.get("serverStatus", 0) == 1
        players = data.get("total")
        return _ok("AionDestiny", "https://aiondestiny.net", "4.6", players, online=is_online)
    except Exception as exc:
        return _err("AionDestiny", "https://aiondestiny.net", "4.6", exc)


# ── helpers ───────────────────────────────────────────────────────────────────

def _ok(name, url, version, players, online=None, metric="in-game", note=None, unavailable=False):
    if online is None:
        online = players is not None
    status = players if players is not None else "N/A"
    print(f"[{name}] {status}")
    return {
        "name": name, "url": url, "version": version,
        "online": online, "players": players,
        "metric": metric, "note": note, "unavailable": unavailable, "error": None,
    }

def _err(name, url, version, exc, metric="in-game", note=None):
    print(f"[ERROR] {name}: {exc}", file=sys.stderr)
    return {
        "name": name, "url": url, "version": version,
        "online": False, "players": None,
        "metric": metric, "note": note, "error": str(exc),
    }


def main():
    scrapers = [
        scrape_euroaion,
        scrape_aionempire,
        scrape_gamezaion,
        scrape_originaion,
        scrape_aionriftshade,
        scrape_aiondestiny,
    ]

    servers = [fn() for fn in scrapers]

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "servers": servers,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\nWrote data.json")


if __name__ == "__main__":
    main()
