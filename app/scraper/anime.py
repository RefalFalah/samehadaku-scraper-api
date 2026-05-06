from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import (
    get_text,
    get_attr,
    parse_genres,
    parse_pagination,
    parse_spe_field,
    parse_spe_links,
)
from app.utils.poster import fetch_anilist
from app.models.schemas import (
    AnimeDetail,
    AnimeRef,
    EpisodeItem,
    BatchLink,
    Genre,
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


def _parse_batch_links(page) -> list[BatchLink]:
    result = []
    for a in page.css(".listbatch > a"):
        href = a.attrib.get("href", "")
        title = a.get_all_text().strip()
        result.append(
            BatchLink(
                title=title,
                slug=extract_slug(href, "batch"),
                url=href,
            )
        )
    return result


async def get_anime_info(slug: str) -> AnimeDetail | None:
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

    genres = parse_genres_from_container(page, ".infoanime .infox .genre-info")

    spe = page
    japanese_name = parse_spe_field(spe, "Japanese")
    english_name = parse_spe_field(spe, "English")
    synonyms = parse_spe_field(spe, "Synonyms")
    status = parse_spe_field(spe, "Status")
    anime_type = parse_spe_field(spe, "Type")
    source = parse_spe_field(spe, "Source")
    duration = parse_spe_field(spe, "Duration")
    total_episodes = parse_spe_field(spe, "Total Episode")
    released = parse_spe_field(spe, "Released")

    season = None
    for span in spe.css(".spe > span"):
        bold = span.css("b")
        if bold and bold[0].text and bold[0].text.strip().lower().startswith("season"):
            links = span.css("a")
            if links:
                href = links[0].attrib.get("href", "")
                season = Genre(
                    name=links[0].text.strip() if links[0].text else "",
                    slug=href.rstrip("/").split("/")[-1],
                    url=href,
                )
            break

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
    batch_links = _parse_batch_links(page)

    anilist = await fetch_anilist(title)
    poster_hd = anilist.get("posterHD") if anilist else None
    if anilist and anilist.get("synopsisHD"):
        synopsis = anilist["synopsisHD"]

    return AnimeDetail(
        title=title,
        japaneseName=japanese_name or None,
        englishName=english_name or None,
        synonyms=synonyms or None,
        poster=poster,
        posterHD=poster_hd,
        score=score or None,
        ratingCount=rating_count or None,
        type=anime_type or None,
        status=status or None,
        source=source or None,
        duration=duration or None,
        episodeCount=total_episodes or None,
        season=season,
        studio=studio,
        producers=producers,
        released=released or None,
        genres=genres,
        synopsis=synopsis,
        episodeLists=episode_lists,
        batchLinks=batch_links,
    )


def parse_genres_from_container(page, selector: str) -> list[Genre]:
    els = page.css(selector)
    if not els:
        return []
    return parse_genres(els[0])


async def get_anime_episodes(slug: str) -> list[EpisodeItem] | None:
    page = await fetch_page(build_url(f"/anime/{slug}/"))
    episodes = _parse_episode_list(page)
    return episodes if episodes else None