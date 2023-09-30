from selectolax.parser import HTMLParser

from .database import City, Street
from scraper_kit.src import html_utils


def parce_cities_index(content: str) -> list[str]:
    dom = HTMLParser(content)
    section = dom.css_first(".b-select-by-cities")
    urls = []
    if section:
        for anchor in section.css("a"):
            name = anchor.text(strip=True)
            href = anchor.attributes["href"].strip("/")
            # print(name + " >> " + anchor.attributes["href"])
            city, created = City.get_or_create(slug=href)
            city.name = name
            city.save()
            urls.append(href)

    return sorted(set(urls))


def parse_city_streets(content: str, city: City) -> list[str]:
    dom = HTMLParser(content)
    urls = []
    for anchor in dom.css('dom.css("#main > .b-area-code table tr a")'):
        name = anchor.text(strip=True)
        href = anchor.attributes["href"].strip("/")
        Street(name=name, slug=href, city=city).save()
        urls.append(href)

    return sorted(set(urls))


def street_next_page(dom: HTMLParser) -> str | None:
    anchors = dom.css("#main .prev-next > a")
    if any(anchors):
        return anchors[-1].attributes["href"]
    return None


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
