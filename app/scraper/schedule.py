from app.scraper.client import fetch_page
from app.config import build_url, extract_slug
from app.utils.parser import get_attr
from app.models.schemas import ScheduleDay, ScheduleAnime


async def get_schedule() -> list[ScheduleDay]:
    page = await fetch_page(build_url("/jadwal-rilis/"))
    result = []

    for day_section in page.css(".kgdt2, .klnr, .hari, .schedule-day, .widget_senction"):
        day_name = ""
        heading = day_section.css("h2, h3, .widget-title span, .day")
        if heading:
            day_name = heading[0].get_all_text().strip()

        if not day_name:
            continue

        anime_list = []
        for li in day_section.css("ul li"):
            a_el = li.css("a")
            if not a_el:
                continue

            href = a_el[0].attrib.get("href", "")
            title = a_el[0].text.strip() if a_el[0].text else ""

            poster = ""
            img_el = li.css("img")
            if img_el:
                poster = img_el[0].attrib.get("src", "") or img_el[0].attrib.get(
                    "data-src", ""
                )

            anime_list.append(
                ScheduleAnime(
                    title=title,
                    slug=extract_slug(href, "anime") if "/anime/" in href else extract_slug(href, ""),
                    poster=poster,
                    url=href,
                )
            )

        if anime_list:
            result.append(ScheduleDay(day=day_name, animeList=anime_list))

    if not result:
        for day_section in page.css(".kgdw, .jadwal, div[id^='hari-'], .day-item"):
            day_name = ""
            heading = day_section.css("h2, h3, h4, .day-title")
            if heading:
                day_name = heading[0].get_all_text().strip()
            if not day_name:
                continue

            anime_list = []
            for li in day_section.css("ul li, .anime-item"):
                a_el = li.css("a")
                if not a_el:
                    continue

                href = a_el[0].attrib.get("href", "")
                title = a_el[0].text.strip() if a_el[0].text else ""

                anime_list.append(
                    ScheduleAnime(
                        title=title,
                        slug=extract_slug(href, "anime") if "/anime/" in href else "",
                        poster=get_attr(li, "img", "src") or get_attr(li, "img", "data-src"),
                        url=href,
                    )
                )

            if anime_list:
                result.append(ScheduleDay(day=day_name, animeList=anime_list))

    return result