import asyncio
import logging

from scrapling.fetchers import Fetcher, StealthyFetcher

logger = logging.getLogger(__name__)

CLOUDFLARE_INDICATORS = [
    "Sorry, you have been blocked",
    "Attention Required! | Cloudflare",
]


def _is_cloudflare_block(page) -> bool:
    try:
        text = page.get_all_text(ignore_tags=("script", "style"))
        return any(indicator in text for indicator in CLOUDFLARE_INDICATORS)
    except Exception:
        return False


async def fetch_page(url: str):
    try:
        page = await asyncio.to_thread(
            Fetcher.get, url, impersonate="chrome", stealthy_headers=True
        )
        if not _is_cloudflare_block(page):
            return page
        logger.info(f"Cloudflare detected on {url}, falling back to StealthyFetcher")
    except Exception as e:
        logger.warning(f"Fetcher failed for {url}: {e}, falling back to StealthyFetcher")

    page = await asyncio.to_thread(StealthyFetcher.fetch, url, headless=True)
    return page