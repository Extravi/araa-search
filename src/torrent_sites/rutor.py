import _config as config
from src import helpers
from urllib.parse import quote


def name():
    return "rutor"


def get_catagory_code(cat):
    catagory_codes = {
        'all': '',
        'movie': '&category=1',
        'tv': '&category=6',
        'games': '&category=8',
        'software': '&category=9',
        'anime': '&category=10',
        'music': '&category=2',
    }

    return catagory_codes.get(cat)


def search(query, catagory="all"):
    catagory = get_catagory_code(catagory)
    if catagory is None:
        return []

    url = f"https://{config.RUTOR_DOMAIN}/search/{quote(query)}{catagory}"
    html = helpers.makeHTMLRequest(url)
    results = []

    for torrent in html.select(".gai, .tum"):
        tds = torrent.find_all("td")
        spans = torrent.find_all("span")
        byte_size = helpers.string_to_bytes(tds[-2].get_text())
        title = tds[1]

        results.append({
            "href": config.RUTOR_DOMAIN,
            "title": title.get_text(),
            "magnet": helpers.apply_trackers(tds[1].find_all("a")[1]["href"]),
            "bytes": byte_size,
            "size": helpers.bytes_to_string(byte_size),
            "seeders": int(spans[0].get_text()),
            "leechers": int(spans[1].get_text()),
            "post_link": f"https://{config.RUTOR_DOMAIN}{title['href']}"
        })

    return results
