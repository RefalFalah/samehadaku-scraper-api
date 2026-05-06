from app.scraper.client import fetch_page
from app.config import build_url
from app.utils.parser import get_text, get_attr, extract_slug, parse_pagination
from app.models.schemas import OngoingAnime


def _parse_ongoing_anime(page) -> list[OngoingAnime]:
    result = []
    for li in page.css(".venz ul li"):
        result.append(
            OngoingAnime(
                title=get_text(li, ".jdlflm"),
                slug=extract_slug(get_attr(li, ".thumb a", "href"), "anime"),
                poster=get_attr(li, ".thumbz img", "src"),
                currentEpisode=get_text(li, ".epz"),
                releaseDay=get_text(li, ".epztipe"),
                newestReleaseDate=get_text(li, ".newnime"),
                url=get_attr(li, ".thumb a", "href"),
            )
        )
    return result


async def get_ongoing_anime(page_num: int = 1):
    page = await fetch_page(build_url(f"/ongoing-anime/page/{page_num}"))
    data = _parse_ongoing_anime(page)
    pagination = parse_pagination(page)
    return {"data": data, "pagination": pagination}