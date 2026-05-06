from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import get_text, get_attr, parse_genres, parse_pagination
from app.models.schemas import Genre, AnimeByGenre


async def get_genre_lists() -> list[Genre]:
    page = await fetch_page(build_url("/daftar-anime-2/?list"))
    result = []

    for a in page.css(".letterlist a, .letter_home a, .az-list a"):
        name = a.text.strip() if a.text else ""
        href = a.attrib.get("href", "")
        if name and href:
            slug = href.rstrip("/").split("/")[-1]
            result.append(Genre(name=name, slug=slug, url=href))

    if not result:
        for a in page.css("ul li a[href*='/genre/']"):
            name = a.text.strip() if a.text else ""
            href = a.attrib.get("href", "")
            if name and href and "/genre/" in href:
                slug = href.rstrip("/").split("/")[-1]
                result.append(Genre(name=name, slug=slug, url=href))

    return result


async def get_anime_by_genre(genre_slug: str, page_num: int = 1):
    url = build_url(f"/genre/{genre_slug}/")
    if page_num > 1:
        url = build_url(f"/genre/{genre_slug}/page/{page_num}/")

    page = await fetch_page(url)
    result = []

    for article in page.css("article.animpost"):
        anime = article.css_first("div.animepost")
        if not anime:
            continue

        link_el = anime.css("div.animposx > a")
        if not link_el:
            continue

        poster = get_attr(anime, "img.anmsa", "src") or get_attr(
            anime, "img.anmsa", "data-src"
        )

        type_val = ""
        type_el = anime.css("div.animposx .content-thumb div.type")
        if type_el:
            type_val = type_el[0].get_all_text().strip()

        score = ""
        score_el = anime.css("div.animposx .content-thumb .score")
        if score_el:
            score_text = score_el[0].get_all_text().strip()
            score = score_text.replace("Rated ", "").strip()

        title = ""
        title_el = anime.css("div.animposx .data .title h2")
        if title_el:
            title = title_el[0].get_all_text().strip()

        status = ""
        status_el = anime.css("div.animposx .data .type")
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

        href = link_el[0].attrib.get("href", "")

        result.append(
            AnimeByGenre(
                title=title,
                slug=extract_slug(href, "anime"),
                poster=poster,
                type=type_val or None,
                score=score or None,
                status=status or None,
                genres=genres,
                synopsis=synopsis or None,
                url=href,
            )
        )

    pagination = parse_pagination(page)
    return {"data": result, "pagination": pagination}