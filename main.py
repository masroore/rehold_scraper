from stash import get_leveldb_lzma_stash, StashOptions
from stash.consts import SIZE_KB
from yarl import URL

from scraper_kit.src import options, utils
from scraper_kit.src.aio_utils import configure_event_loop
from scraper_kit.src.proxies import RotatingProxyPool
from scraper_kit.src.sessions import SessionManager
from scraper_kit.src.timer import Timer
from scraper_kit.src.web.task import TaskResult, TaskRequest
from scraper_kit.src.web.worker import AsyncWebWorker, SyncWebWorker
from src import urls, parser, fetcher, database
from src.database import City

CITIES: list[str] = []


def parse_index_page(content: str | bytes):
    global CITIES
    cities = parser.parce_cities_index(content)
    CITIES.extend(cities)


def process_download(response: TaskResult, _: AsyncWebWorker):
    global task_queue, cache, timer
    # print(response.url)
    content_len = 0
    tag: str = response.tag

    # print(response.content)
    if response.is_error:
        # utils.croak(response.exception)
        pass
    else:
        if response.content and response.status_code == 200:
            content_len = len(response.content)

            bleached = parser.peroxide(
                html=response.content, retain_scripts=False, minify=True
            )
            cache.write(tag, content=bleached)
            slug = tag.split("@")[1]
            if tag.startswith("ix@"):
                parse_index_page(content=response.content)
            elif tag.startswith("cy@"):
                parse_city_page(content=response.content, slug=slug)

    if response.proxy_server:
        purl = URL(response.proxy_server)
        # proxy = "{0}:{1}".format(purl.host, purl.port)
        proxy = purl.host
    else:
        proxy = ""

    elapsed = "{:.1f}".format(round(response.elapsed_time, 1))
    utils.croak(
        f"Tm: {elapsed:>5} | Ht: {response.status_code} | Dl: {utils.human_size(content_len, suppress_zero=True):>8} | {tag}",
        timer=timer,
    )


def parse_city_page(content: str | bytes, slug: str):
    print(slug)
    city = City.get_or_none(slug=slug)
    streets = parser.parse_city_streets(content=content, city=city)


if __name__ == "__main__":
    configure_event_loop()
    options.load_options()

    database.init_db()

    opt = StashOptions()
    opt.cache_min_size = SIZE_KB * 1
    cache = get_leveldb_lzma_stash(opt)

    sessions = SessionManager()
    concurrency = options.get_options().concurrency
    proxies = RotatingProxyPool(
        rotating_proxy=options.get_options().rotating_proxy, concurrency=concurrency
    )
    worker = AsyncWebWorker(
        concurrency=concurrency,
        proxy_man=proxies,
        session_man=sessions,
        timer=Timer(),
        timeout=options.get_options().timeout,
    )
    worker.set_result_available_hook(process_download)

    """
    generator = CfWorkitemGenerator(
        "https://stevemorse.hopto.org/",
        backend_server_urls=["https://stevemorse.hopto.org/"],
        proxies=proxies,
    )
    """

    loader = fetcher.MultiFetcher(
        workers=worker,
        concurrency=concurrency,
        proxies=proxies,
    )

    task_queue: list[str] = []
    utils.croak(f"Concurrency: {concurrency}")
    timer = Timer().start()

    for u in urls.city_indices():
        tag = "ix@" + u
        if cache.exists(tag):
            content = cache.read(tag)
            parse_index_page(content=content)
        else:
            loader.add_task(
                TaskRequest(
                    url=u,
                    session_disabled=True,
                    session_id="",
                    tag=tag,
                    proxy_url=proxies.pick(),
                    proxy_disabled=True,
                )
            )

    loader.run()
    CITIES = sorted(set(CITIES))

    for c_slug in CITIES:
        slugs = urls.append_alpha_num(c_slug + "+", True)
        for slug in slugs:
            url = urls.city_url(slug)
            tag = "cy@" + c_slug

            if cache.exists(tag):
                content = cache.read(tag)
                parse_city_page(content=content, slug=c_slug)
            else:
                loader.add_task(
                    TaskRequest(
                        url=url,
                        session_disabled=True,
                        session_id="",
                        tag=tag,
                        proxy_url=proxies.pick(),
                        proxy_disabled=True,
                    )
                )

    loader.run()
