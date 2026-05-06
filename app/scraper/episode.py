from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import get_text, get_attr, parse_download_groups
from app.models.schemas import EpisodeDetail, AnimeRef, DownloadGroup


async def get_episode_by_slug(slug: str) -> EpisodeDetail | None:
    url = build_url(f"/{slug}/")
    page = await fetch_page(url)

    title_el = page.css("header.info_episode h1.entry-title")
    title = title_el[0].text.strip() if title_el else ""
    if not title:
        return None

    stream_url = get_attr(page, "#pembed iframe", "src") or get_attr(
        page, ".mfp-hide iframe", "src"
    )

    download_urls = []
    for dl_div in page.css(".download-eps"):
        ul_list = dl_div.css("ul")
        if ul_list:
            download_urls.extend(parse_download_groups(dl_div, "ul li"))

    prev_slug = ""
    next_slug = ""
    nav_els = page.css(".naveps .nvsc a")
    if nav_els:
        for a in nav_els:
            href = a.attrib.get("href", "")
            text = a.text.strip() if a.text else ""
            if "prev" in (a.attrib.get("class", "") + text).lower() or text.startswith(
                "«"
            ):
                prev_slug = extract_slug(href, "")
            elif "next" in (a.attrib.get("class", "") + text).lower() or text.endswith(
                "»"
            ):
                next_slug = extract_slug(href, "")

    anime_title = ""
    anime_slug = ""
    breadcrumb = page.css("#breadcrumbs ol li a")
    if len(breadcrumb) >= 2:
        anime_title = breadcrumb[-1].text.strip() if breadcrumb[-1].text else ""
        href = breadcrumb[-1].attrib.get("href", "")
        if "/anime/" in href:
            anime_slug = extract_slug(href, "anime")
        else:
            for crumb in breadcrumb:
                crumb_href = crumb.attrib.get("href", "")
                if "/anime/" in crumb_href:
                    anime_slug = extract_slug(crumb_href, "anime")
                    anime_title = crumb.text.strip() if crumb.text else ""
                    break

    previous_episode = None
    if prev_slug:
        previous_episode = AnimeRef(
            title="",
            slug=prev_slug,
            url=build_url(f"/{prev_slug}/"),
        )

    next_episode = None
    if next_slug:
        next_episode = AnimeRef(
            title="",
            slug=next_slug,
            url=build_url(f"/{next_slug}/"),
        )

    return EpisodeDetail(
        title=title,
        anime=AnimeRef(
            title=anime_title,
            slug=anime_slug,
            url=build_url(f"/anime/{anime_slug}/") if anime_slug else "",
        ),
        streamUrl=stream_url or None,
        downloadUrls=download_urls,
        hasNextEpisode=next_episode is not None,
        nextEpisode=next_episode,
        hasPreviousEpisode=previous_episode is not None,
        previousEpisode=previous_episode,
    )