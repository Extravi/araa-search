from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "tpb"

def search(query):
    url = f"https://{API_BAY_DOMAIN}/q.php?q={quote(query)}&cat="
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
