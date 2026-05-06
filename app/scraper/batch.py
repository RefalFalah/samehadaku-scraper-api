from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import get_text, get_attr, parse_batch_download_groups
from app.models.schemas import BatchDetail, BatchDownloadGroup, DownloadLink
from app.scraper.anime import get_anime_info


async def get_batch_by_slug(slug: str) -> BatchDetail | None:
    page = await fetch_page(build_url(f"/batch/{slug}/"))

    title_el = page.css(".entry-title")
    title = title_el[0].text.strip() if title_el else ""
    if not title:
        return None

    download_urls = parse_batch_download_groups(page, ".download ul li")

    return BatchDetail(title=title, downloadUrls=download_urls)


async def get_batch_by_anime_slug(anime_slug: str) -> BatchDetail | None:
    anime_info = await get_anime_info(anime_slug)
    if not anime_info or not anime_info.batchLinks:
        return None

    first_batch = anime_info.batchLinks[0]
    return await get_batch_by_slug(first_batch.slug)