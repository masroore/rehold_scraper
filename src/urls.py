import string

_BASE_URL = "https://rehold.com"


def append_alpha_num(base_url: str, include_num: bool) -> list[str]:
    urls = []
    if include_num:
        urls.append(base_url + "1")
    for c in string.ascii_uppercase:
        urls.append(base_url + c)
    return urls


def city_indices() -> list[str]:
    return append_alpha_num(_BASE_URL + "/NJ+", False)
