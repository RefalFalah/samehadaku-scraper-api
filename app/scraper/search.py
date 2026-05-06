from urllib.parse import quote

from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import get_text, get_attr, parse_genres
from app.models.schemas import SearchAnime, Genre


async def search_anime(keyword: str) -> list[SearchAnime]:
    encoded = quote(keyword)
    page = await fetch_page(build_url(f"/?s={encoded}&post_type=anime"))
    result = []

    for article in page.css("article.animpost"):
        anime_list = article.css("div.animepost")
        anime = anime_list[0] if anime_list else None
        if not anime:
            continue

        link_el = anime.css("div.animposx > a")
        if not link_el:
            continue
        link = link_el[0]

        poster = ""
        img_el = link.css("img.anmsa")
        if img_el:
            poster = img_el[0].attrib.get("src", "") or img_el[0].attrib.get("data-src", "")

        type_val = ""
        type_el = link.css("div.type")
        if type_el:
            type_val = type_el[0].get_all_text().strip()

        score = ""
        score_el = link.css(".score")
        if score_el:
            score_text = score_el[0].get_all_text().strip()
            score = score_text.replace("Rated ", "").strip()

        title = ""
        title_el = link.css(".data .title h2")
        if title_el:
            title = title_el[0].get_all_text().strip()

        status = ""
        status_el = link.css(".data .type")
        if status_el:
            status = status_el[0].get_all_text().strip()

        synopsis = ""
        synopsis_el = anime.css(".stooltip .ttls")
        if synopsis_el:
            synopsis = synopsis_el[0].get_all_text().strip()

        genres = []
        genre_el = anime.css(".stooltip .genres .mta")
        if genre_el:
            genres = parse_genres(genre_el[0])

        href = link.attrib.get("href", "")

        result.append(
            SearchAnime(
                title=title,
                slug=extract_slug(href, "anime"),
                poster=poster,
                type=type_val or None,
                score=score or None,
                status=status or None,
                synopsis=synopsis or None,
                genres=genres,
                url=href,
            )
        )

    return result