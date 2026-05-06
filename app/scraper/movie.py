from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import (
    get_text,
    get_attr,
    parse_genres,
    parse_pagination,
    parse_spe_field,
    parse_download_groups,
)
from app.models.schemas import (
    MovieListItem,
    MovieDetail,
    EpisodeItem,
    BatchLink,
    Genre,
)


async def get_movies(page_num: int = 1, order: str = "update"):
    url = build_url("/daftar-anime-2/")
    if page_num > 1:
        url = build_url(f"/daftar-anime-2/page/{page_num}/")
    url = f"{url}?type=Movie&order={order}"

    page = await fetch_page(url)
    data = _parse_movie_list(page)
    pagination = parse_pagination(page)
    return {"data": data, "pagination": pagination}


def _parse_movie_list(page) -> list[MovieListItem]:
    result = []
    for article in page.css("article.animpost"):
        anime_els = article.css("div.animepost")
        if not anime_els:
            continue

        link_el = anime_els[0].css("div.animposx > a")
        if not link_el:
            continue
        link = link_el[0]

        type_val = ""
        type_el = link.css("div.type")
        if type_el:
            type_val = type_el[0].get_all_text().strip()

        poster = get_attr(anime_els[0], "img.anmsa", "src") or get_attr(
            anime_els[0], "img.anmsa", "data-src"
        )

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
        synopsis_el = anime_els[0].css(".stooltip .ttls")
        if synopsis_el:
            synopsis = synopsis_el[0].get_all_text().strip()

        genres = []
        genre_el = anime_els[0].css(".stooltip .genres .mta")
        if genre_el:
            genres = parse_genres(genre_el[0])

        href = link.attrib.get("href", "")

        result.append(
            MovieListItem(
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
    return result


async def get_movie_info(slug: str) -> MovieDetail | None:
    page = await fetch_page(build_url(f"/anime/{slug}/"))

    title_el = page.css("header.info_episode h1.entry-title")
    if not title_el:
        return None
    title = title_el[0].text.strip() if title_el[0].text else ""

    poster = get_attr(page, ".infoanime .thumb img.anmsa", "src") or get_attr(
        page, ".infoanime .thumb img", "src"
    )

    score = get_text(page, ".rtg span[itemprop='ratingValue']")
    rating_count = ""
    rc_el = page.css("i[itemprop='ratingCount']")
    if rc_el:
        rating_count = rc_el[0].attrib.get("content", "")

    synopsis = get_text(page, ".infoanime .infox .desc .entry-content-single p")

    genres = _parse_genres_from_container(page, ".infoanime .infox .genre-info")

    spe = page
    japanese_name = parse_spe_field(spe, "Japanese")
    english_name = parse_spe_field(spe, "English")
    synonyms = parse_spe_field(spe, "Synonyms")
    status = parse_spe_field(spe, "Status")
    source = parse_spe_field(spe, "Source")
    duration = parse_spe_field(spe, "Duration")
    released = parse_spe_field(spe, "Released")

    studio = None
    for span in spe.css(".spe > span"):
        bold = span.css("b")
        if bold and bold[0].text and bold[0].text.strip().lower().startswith("studio"):
            links = span.css("a")
            if links:
                href = links[0].attrib.get("href", "")
                studio = Genre(
                    name=links[0].text.strip() if links[0].text else "",
                    slug=href.rstrip("/").split("/")[-1],
                    url=href,
                )
            break

    producers = []
    for span in spe.css(".spe > span"):
        bold = span.css("b")
        if bold and bold[0].text and bold[0].text.strip().lower().startswith("producer"):
            for a in span.css("a"):
                href = a.attrib.get("href", "")
                producers.append(
                    Genre(
                        name=a.text.strip() if a.text else "",
                        slug=href.rstrip("/").split("/")[-1],
                        url=href,
                    )
                )
            break

    episode_lists = _parse_episode_list(page)

    download_urls = []
    for dl_div in page.css(".download-eps"):
        ul_list = dl_div.css("ul")
        if ul_list:
            download_urls.extend(parse_download_groups(dl_div, "ul li"))

    return MovieDetail(
        title=title,
        japaneseName=japanese_name or None,
        englishName=english_name or None,
        synonyms=synonyms or None,
        poster=poster,
        score=score or None,
        ratingCount=rating_count or None,
        status=status or None,
        source=source or None,
        duration=duration or None,
        released=released or None,
        studio=studio,
        producers=producers,
        genres=genres,
        synopsis=synopsis,
        episodeLists=episode_lists,
        downloadUrls=download_urls,
    )


def _parse_episode_list(page) -> list[EpisodeItem]:
    result = []
    for li in page.css(".lstepsiode.listeps > ul > li"):
        eps_a = li.css(".epsright .eps a")
        lchx_a = li.css(".epsleft .lchx a")
        date_el = li.css(".epsleft .date")

        if not eps_a and not lchx_a:
            continue

        a_el = lchx_a[0] if lchx_a else (eps_a[0] if eps_a else None)
        if not a_el:
            continue

        href = a_el.attrib.get("href", "")

        number = ""
        if eps_a:
            number = eps_a[0].text.strip() if eps_a[0].text else ""

        title = a_el.text.strip() if a_el.text else ""
        date = date_el[0].text.strip() if date_el else ""

        result.append(
            EpisodeItem(
                number=number,
                title=title,
                slug=extract_slug(href, ""),
                date=date,
                url=href,
            )
        )
    result.reverse()
    return result


def _parse_genres_from_container(page, selector: str) -> list[Genre]:
    els = page.css(selector)
    if not els:
        return []
    return parse_genres(els[0])