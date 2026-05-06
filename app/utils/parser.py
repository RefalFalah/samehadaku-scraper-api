import re

from app.models.schemas import (
    Genre,
    DownloadGroup,
    DownloadLink,
    Pagination,
    BatchDownloadGroup,
)


def get_text(element, selector: str, default: str = "") -> str:
    results = element.css(selector)
    if results:
        return results[0].get_all_text().strip()
    return default


def get_attr(element, selector: str, attr: str, default: str = "") -> str:
    results = element.css(selector)
    if results:
        return results[0].attrib.get(attr, default)
    return default


def parse_genres(element) -> list[Genre]:
    genres = []
    for a in element.css("a"):
        name = a.text.strip() if a.text else ""
        href = a.attrib.get("href", "")
        if name and href:
            slug = href.rstrip("/").split("/")[-1]
            genres.append(Genre(name=name, slug=slug, url=href))
    return genres


def parse_genres_from_container(element, selector: str) -> list[Genre]:
    els = element.css(selector)
    if not els:
        return []
    return parse_genres(els[0])


def parse_pagination(page) -> Pagination | None:
    current_el = page.css(".page-numbers.current")
    if not current_el:
        return None

    try:
        current_page = int(current_el[0].text.strip())
    except (ValueError, AttributeError):
        return None

    last_page = current_page

    page_info = page.css(".pagination span")
    for span in page_info:
        text = span.text.strip() if span.text else ""
        m = re.match(r"Page\s+\d+\s+of\s+(\d+)", text, re.IGNORECASE)
        if m:
            last_page = int(m.group(1))
            break

    if last_page <= current_page:
        for el in page.css(".pagination a"):
            href = el.attrib.get("href", "")
            m = re.search(r"/page/(\d+)/?", href)
            if m:
                num = int(m.group(1))
                if num > last_page:
                    last_page = num

    return Pagination(
        currentPage=current_page,
        lastVisiblePage=last_page,
        hasNextPage=current_page < last_page,
        nextPage=current_page + 1 if current_page < last_page else None,
        hasPreviousPage=current_page > 1,
        previousPage=current_page - 1 if current_page > 1 else None,
    )


def parse_download_groups(element, selector: str) -> list[DownloadGroup]:
    result = []
    for li in element.css(selector):
        links = []
        for a in li.css("a"):
            links.append(
                DownloadLink(
                    provider=a.text.strip() if a.text else "",
                    url=a.attrib.get("href", ""),
                )
            )

        strong_els = li.css("strong")
        resolution = strong_els[0].text.strip() if strong_els else ""
        resolution = re.sub(r"^[A-Za-z]{2,3}\s?", "", resolution).strip()

        result.append(DownloadGroup(resolution=resolution, urls=links))
    return result


def parse_batch_download_groups(element, selector: str) -> list[BatchDownloadGroup]:
    result = []
    for li in element.css(selector):
        links = []
        for a in li.css("a"):
            links.append(
                DownloadLink(
                    provider=a.text.strip() if a.text else "",
                    url=a.attrib.get("href", ""),
                )
            )

        strong_els = li.css("strong")
        resolution = strong_els[0].text.strip() if strong_els else ""
        resolution = re.sub(r"^[A-Za-z]{2,3}\s?", "", resolution).strip()

        i_els = li.css("i")
        file_size = i_els[0].text.strip() if i_els else ""

        result.append(
            BatchDownloadGroup(resolution=resolution, fileSize=file_size, urls=links)
        )
    return result


_REPLACEMENTS = {
    "yang lalu": "ago",
    "menit yang lalu": "minutes ago",
    "jam yang lalu": "hours ago",
    "hari yang lalu": "days ago",
    "minggu yang lalu": "weeks ago",
    "bulan yang lalu": "months ago",
    "tahun yang lalu": "years ago",
    "menit": "minute",
    "jam": "hour",
    "hari": "day",
    "minggu": "week",
    "bulan": "month",
    "tahun": "year",
    "Posted by:": "Posted by:",
    "Released on:": "",
    "Released on": "",
}


def normalize_date(text: str) -> str:
    text = text.strip()
    for id_text, en_text in _REPLACEMENTS.items():
        text = text.replace(id_text, en_text)
    text = re.sub(r"^[^A-Za-z0-9]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_slug(url: str, prefix: str) -> str:
    pattern = re.compile(rf"^https?://[^/]+/{prefix}/")
    return pattern.sub("", url).rstrip("/")


def parse_spe_field(element, label: str) -> str:
    for span in element.css(".spe > span"):
        text = span.get_all_text()
        bold = span.css("b")
        label_text = bold[0].text.strip() if bold else ""
        if label_text.lower().startswith(label.lower()):
            value = text
            for b in bold:
                b_text = b.text.strip() if b.text else ""
                value = value.replace(b_text, "").strip()
            return value.strip().rstrip(":").strip()
    return ""


def parse_spe_links(element, label: str) -> list:
    for span in element.css(".spe > span"):
        bold = span.css("b")
        label_text = bold[0].text.strip() if bold else ""
        if label_text.lower().startswith(label.lower()):
            return parse_genres(span)
    return []