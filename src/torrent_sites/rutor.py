from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "rutor"

def search(query):
    url = f"https://{RUTOR_DOMAIN}/search/{quote(query)}"
    html = helpers.makeHTMLRequest(url)
    results = []

    for torrent in html.select(".gai, .tum"):
        tds = torrent.find_all("td")
        spans = torrent.find_all("span")

        results.append({
            "href": RUTOR_DOMAIN,
            "title": tds[1].get_text(),
            "magnet": helpers.apply_trackers(tds[1].find_all("a")[1]["href"]),
            "size": tds[-2].get_text(),
            "views": None,
            "seeders": int(spans[0].get_text()),
            "leechers": int(spans[1].get_text()),
        })

    return results
