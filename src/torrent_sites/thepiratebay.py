from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "tpb"

def convert_bytes(size):
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"

def search(query):
    url = f"https://{API_BAY_DOMAIN}/q.php?q={quote(query)}&cat="
    torrent_data = helpers.makeJSONRequest(url)
    results = []

    for torrent in torrent_data:
        results.append({
            "href": "thepiratebay.org",
            "title": torrent["name"],
            "magnet": helpers.apply_trackers(
                torrent["info_hash"],
                name=torrent["name"],
                magnet=False
            ),
            "size": convert_bytes(int(torrent["size"])),
            "views": None,
            "seeders": int(torrent["seeders"]),
            "leechers": int(torrent["leechers"])
        })

    return results
