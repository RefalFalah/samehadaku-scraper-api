import asyncio

from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import get_text, get_attr, normalize_date, parse_spe_field
from app.utils.poster import fetch_anilist
from app.models.schemas import RecentAnime, TopAnime


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


def _parse_top_10(page) -> list[TopAnime]:
    result = []
    for li in page.css(".topten-animesu > ul > li"):
        series_el = li.css("a.series")
        if not series_el:
            continue
        series = series_el[0]

        title = ""
        judul_el = series.css("span.judul")
        if judul_el:
            title = judul_el[0].text.strip() if judul_el[0].text else ""

        score = ""
        rating_el = series.css("span.rating")
        if rating_el:
            score = rating_el[0].get_all_text().strip()

        poster = series.attrib.get("href", "")
        img_el = series.css("img")
        poster_src = ""
        if img_el:
            poster_src = img_el[0].attrib.get("src", "") or img_el[0].attrib.get("data-src", "")

        href = series.attrib.get("href", "")
        rank = len(result) + 1

        result.append(
            TopAnime(
                rank=rank,
                title=title,
                slug=extract_slug(href, "anime") if "/anime/" in href else extract_slug(href, ""),
                poster=poster_src,
                score=score or None,
                url=href,
            )
        )
    return result


async def get_home():
    page = await fetch_page(build_url("/"))
    recent = _parse_recent_list(page)
    top = _parse_top_10(page)
    slugs = [a.slug for a in top]
    details = await asyncio.gather(*[_fetch_top_detail(s) for s in slugs])
    for anime, detail in zip(top, details):
        if detail:
            anime.episodeCount = detail.get("episodeCount")
            anime.status = detail.get("status")
            anime.synopsis = detail.get("synopsisHD") or detail.get("synopsis")
            anime.posterHD = detail.get("posterHD")
    return {"recentAnime": recent, "topAnime": top}


async def get_top_anime():
    page = await fetch_page(build_url("/"))
    top = _parse_top_10(page)
    slugs = [a.slug for a in top]
    details = await asyncio.gather(*[_fetch_top_detail(s) for s in slugs])
    for anime, detail in zip(top, details):
        if detail:
            anime.episodeCount = detail.get("episodeCount")
            anime.status = detail.get("status")
            anime.synopsis = detail.get("synopsisHD") or detail.get("synopsis")
            anime.posterHD = detail.get("posterHD")
    return top


async def _fetch_top_detail(slug: str) -> dict | None:
    try:
        page = await fetch_page(build_url(f"/anime/{slug}/"))
        if not page.css("header.info_episode h1.entry-title"):
            return None
        title_el = page.css("header.info_episode h1.entry-title")
        title = title_el[0].text.strip() if title_el and title_el[0].text else ""
        episode_count = parse_spe_field(page, "Total Episode")
        episode_count = (episode_count or "").strip()
        if not episode_count.isdigit():
            episode_count = str(len(page.css(".lstepsiode.listeps > ul > li")))
        status = parse_spe_field(page, "Status")
        synopsis = get_text(page, ".infoanime .infox .desc .entry-content-single p")
        anilist = await fetch_anilist(title) if title else None
        poster_hd = anilist.get("posterHD") if anilist else None
        synopsis_hd = anilist.get("synopsisHD") if anilist else None
        return {
            "episodeCount": episode_count,
            "status": status or None,
            "synopsis": synopsis or None,
            "posterHD": poster_hd,
            "synopsisHD": synopsis_hd,
        }
    except Exception:
        return None