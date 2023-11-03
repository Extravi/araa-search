from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "nyaa"

def get_catagory_code(cat):
    match cat:
        case "all":
            return ""
        case "anime":
            return "&c=1_0"
        case "music":
            return "&c=2_0"
        case "game":
            return "&c=6_2"
        case "software":
            return "&c=6_1"
        case _:
            return "ignore"


def search(query, catagory="all"):
    catagory = get_catagory_code(catagory)
    if catagory == "ignore":
        return []

    soup = helpers.makeHTMLRequest(f"https://{NYAA_DOMAIN}/?f=0&q={quote(query)}{catagory}")
    results = []
    for torrent in soup.select(".default, .success, .danger"):
        list_of_tds = torrent.find_all("td")
        byte_size = helpers.string_to_bytes(list_of_tds[3].get_text().strip())

        results.append({
            "href": NYAA_DOMAIN,
            "title": list_of_tds[1].find_all("a")[-1].get_text(),
            "magnet": helpers.apply_trackers(list_of_tds[2].find_all("a")[-1]["href"]),
            "bytes": byte_size,
            "size": helpers.bytes_to_string(byte_size),
            "views": None,
            "seeders": int(list_of_tds[5].get_text().strip()),
            "leechers": int(list_of_tds[6].get_text().strip())
        })
    return results
