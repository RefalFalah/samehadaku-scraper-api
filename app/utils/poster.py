import asyncio
import json
import logging
import re

from scrapling.fetchers import Fetcher

logger = logging.getLogger(__name__)

_ANILIST_URL = "https://graphql.anilist.co"
_CACHE: dict[str, dict] = {}

_TITLE_CLEANUP = re.compile(r"\s*(?:sub\s*indo|subtitle\s*indonesia|batch)$", re.IGNORECASE)


def _clean_title(title: str) -> str:
    cleaned = _TITLE_CLEANUP.sub("", title).strip()
    return cleaned if cleaned else title


def _search_anilist(title: str) -> dict | None:
    search_title = _clean_title(title)
    if search_title in _CACHE:
        return _CACHE[search_title]

    query = "query($search: String) { Media(search: $search, type: ANIME, isAdult: false) { id title { romaji english } coverImage { large extraLarge } } }"
    payload = json.dumps({"query": query, "variables": {"search": search_title}})

    try:
        result = Fetcher.post(
            _ANILIST_URL,
            data=payload,
            impersonate="chrome",
            stealthy_headers=True,
            headers={"Content-Type": "application/json"},
        )
        body = result.body if result.body else b""
        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")
        data = json.loads(body) if body else {}
        media = data.get("data", {}).get("Media")
        if media:
            _CACHE[search_title] = media
        return media
    except Exception:
        return None


async def fetch_poster(title: str) -> str | None:
    if not title:
        return None
    result = await asyncio.to_thread(_search_anilist, title)
    if not result:
        return None
    cover = result.get("coverImage", {})
    return cover.get("extraLarge") or cover.get("large")