from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "nyaa"

def search(query):
    soup = helpers.makeHTMLRequest(f"https://{NYAA_DOMAIN}/?f=0&c=0_0&q={quote(query)}")
    results = []
    for torrent in soup.select(".default, .success, .danger"):
        list_of_tds = torrent.find_all("td")
        results.append({
            "href": NYAA_DOMAIN,
            "title": list_of_tds[1].find_all("a")[-1].get_text(),
            "magnet": helpers.apply_trackers(list_of_tds[2].find_all("a")[-1]["href"]),
            "size": list_of_tds[3].get_text().strip(),
            "views": None,
            "seeders": int(list_of_tds[5].get_text().strip()),
            "leechers": int(list_of_tds[6].get_text().strip())
        })
    return results
