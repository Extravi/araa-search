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
        tds = torrent.findall("td")
        
        # If a torrent has comments, it has 5 columns, but if it has none,
        # it has 4 columns. This is a shift to account for that.
        td_shift = len(tds) - 4

        results.append({
            "href": RUTOR_DOMAIN,
            "title": tds[1].get_text(),
            "magnet": tds[1].findall("a")[1]["href"],
            "size": tds[2 + td_shift].get_text(),
            "views": None,
            "seeders": int(tds[3 + td_shift].find("span", {"class": "green"}).get_text()),
            "leechers": int(tds[3 + td_shift].find("span", {"class": "green"}).get_text()),
        })

    return results
