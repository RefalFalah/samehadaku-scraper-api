from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import get_attr, normalize_date, parse_pagination
from app.models.schemas import RecentAnime


def _parse_recent_list(page) -> list[RecentAnime]:
    result = []
    for li in page.css(".post-show > ul > li"):
        title_el = li.css("h2.entry-title a")
        if not title_el:
            continue

        episode = ""
        author_els = li.css(".dtla author")
        if author_els:
            episode = author_els[0].text.strip() if author_els[0].text else ""

        date = ""
        span_els = li.css(".dtla span")
        if span_els:
            date = normalize_date(span_els[-1].get_all_text())

        poster = get_attr(li, ".thumb img", "src") or get_attr(li, ".thumb img", "data-src")

        result.append(
            RecentAnime(
                title=title_el[0].text.strip() if title_el[0].text else "",
                slug=extract_slug(title_el[0].attrib.get("href", ""), "anime"),
                poster=poster,
                episode=episode,
                date=date or None,
                url=title_el[0].attrib.get("href", ""),
            )
        )
    return result


async def get_recent_anime(page_num: int = 1):
    url = build_url("/anime-terbaru/")
    if page_num > 1:
        url = build_url(f"/anime-terbaru/page/{page_num}/")

    page = await fetch_page(url)
    data = _parse_recent_list(page)
    pagination = parse_pagination(page)
    return {"data": data, "pagination": pagination}