from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "tpb"

def get_catagory_code(cat):
    match cat:
        case "all":
            return ""
        case "audiobook":
            return "102"
        case "movie":
            return "201" 
        case "tv":
            return "205"
        case "games":
            return "400"
        case "software":
            return "300"
        case "anime":
            # TPB has no anime catagory.
            return "ignore"
        case "music":
            return "100"
        case "xxx":
            safesearch = (request.cookies.get("safe", "active") == "active")
            if safesearch:
                return "ignore"
            return "500"
        case _:
            return ""

def search(query, catagory="all"):
    catagory = get_catagory_code(catagory)
    if catagory == "ignore":
        return []

    url = f"https://{API_BAY_DOMAIN}/q.php?q={quote(query)}&cat={catagory}"
    torrent_data = helpers.makeJSONRequest(url)
    results = []

    for torrent in torrent_data:
        byte_size = int(torrent["size"])
        results.append({
            "href": "thepiratebay.org",
            "title": torrent["name"],
            "magnet": helpers.apply_trackers(
                torrent["info_hash"],
                name=torrent["name"],
                magnet=False
            ),
            "bytes": byte_size,
            "size": helpers.bytes_to_string(byte_size),
            "views": None,
            "seeders": int(torrent["seeders"]),
            "leechers": int(torrent["leechers"])
        })

    return results
