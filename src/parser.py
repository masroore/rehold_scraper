from selectolax.parser import HTMLParser
from .urls import _BASE_URL
from scraper_kit.src import html_utils


def parce_cities_index(content: str) -> list[str]:
    dom = HTMLParser(content)
    section = dom.css_first(".b-select-by-cities")
    urls = []
    if section:
        for anchor in section.css("a"):
            urls.append(_BASE_URL + anchor.attributes["href"])

    return sorted(set(urls))


def peroxide(
    html: str | bytes, retain_scripts: bool, minify: bool = False
) -> str | None:
    _unwanted_tags = [
        "style",
        "head",
        "svg",
        "button",
        "noscript",
        "header",
        "footer",
        "input",
        "select",
        "form",
        "ol",
        "link",
        "ul",
        "i",
    ]

    if not retain_scripts:
        _unwanted_tags.append("script")

    bleacher = html_utils.Peroxide(html)
    bleacher.strip_tags(_unwanted_tags, True)
    bleacher.strip_selectors(
        [
            "#mobile-menu",
            "#cookieConsent",
            "#search-result-style-1",
            "#results-person-detailed-style-1",
            "#search",
            ".info-wrapper",
        ],
        True,
    )

    bleacher.strip_attributes(
        ["style", "onmouseover", "onmouseout", "data-aa-adunit", "data-aaad"]
    )

    for script in bleacher.get_root_node().css("script"):
        code = script.text(strip=True).strip()
        if '"@type": "Person"' not in code:
            script.decompose(recursive=True)

    return bleacher.html(minify=minify)
