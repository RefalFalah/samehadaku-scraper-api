import asyncio
import re

from scrapling.fetchers import Fetcher

from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import get_text, get_attr, parse_download_groups
from app.models.schemas import EpisodeDetail, AnimeRef, DownloadGroup, StreamMirror


async def _fetch_stream_mirrors(page, post_id: str) -> list[StreamMirror]:
    mirrors = []
    options = page.css(".east_player_option")
    if not options:
        return mirrors

    ajax_url = build_url("/wp-admin/admin-ajax.php")
    referer = page.url if hasattr(page, "url") else build_url("/")

    async def fetch_mirror(opt):
        nume = opt.attrib.get("data-nume", "")
        post = opt.attrib.get("data-post", post_id)
        dtype = opt.attrib.get("data-type", "schtml")
        span_el = opt.css("span")
        label = span_el[0].text.strip() if span_el and span_el[0].text else opt.text.strip() if opt.text else ""
        if not nume:
            return None
        try:
            result = await asyncio.to_thread(
                Fetcher.post,
                ajax_url,
                data={"action": "player_ajax", "post": post, "nume": nume, "type": dtype},
                impersonate="chrome",
                stealthy_headers=True,
                headers={"Referer": referer},
            )
            body = result.body if result.body else b""
            if isinstance(body, bytes):
                html = body.decode("utf-8", errors="replace")
            else:
                html = str(body)
            src_match = re.search(r'src=["\']([^"\']+)["\']', html)
            if src_match:
                return StreamMirror(quality=label, url=src_match.group(1))
        except Exception:
            pass
        return None

    results = await asyncio.gather(*[fetch_mirror(opt) for opt in options[:6]])
    for r in results:
        if r:
            mirrors.append(r)
    return mirrors


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

    post_id = ""
    first_opt = page.css(".east_player_option")
    if first_opt:
        post_id = first_opt[0].attrib.get("data-post", "")

    stream_mirrors = await _fetch_stream_mirrors(page, post_id)
    if not stream_url and stream_mirrors:
        stream_url = stream_mirrors[0].url

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
        streamMirrors=stream_mirrors,
        downloadUrls=download_urls,
        hasNextEpisode=next_episode is not None,
        nextEpisode=next_episode,
        hasPreviousEpisode=previous_episode is not None,
        previousEpisode=previous_episode,
    )