from _config import *
from src import helpers

def name():
    return "nyaa"

def search(query):
    soup = helpers.makeHTMLRequest(f"https://{NYAA_DOMAIN}/?f=0&c=0_0&q={query}")
    results = []
    for torrent in soup.select(".default, .success, .danger"):
        list_of_anchors = torrent.select("a")
        text_center = torrent.select(".text-center")
        results.append({
            "href": NYAA_DOMAIN,
            "title": list_of_anchors[1].get_text().strip(),
            "magnet": list_of_anchors[1]["href"],
            "size": text_center[1].get_text().strip(),
            "views": None,
            "seeders": int(text_center[3].get_text().strip()),
            "leechers": int(text_center[4].get_text().strip())
        })
    return results
