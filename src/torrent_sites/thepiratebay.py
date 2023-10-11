from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "tpb"

def generate_magnet_link(info_hash):
    return f"magnet:?xt=urn:btih:{info_hash}&tr=http://nyaa.tracker.wf:7777/announce&tr=udp://open.stealth.si:80/announce&tr=udp://tracker.opentrackr.org:1337/announce&tr=udp://exodus.desync.com:6969/announce&tr=udp://tracker.torrent.eu.org:451/announce"

def convert_bytes(size):
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"

def search(query):
    url = f"https://{API_BAY_DOMAIN}/q.php?q={quote(query)}&cat="
    torrent_data = helpers.makeHTMLRequest(url)
    results = []

    for torrent in torrent_data:
        results.append({
            "href": "thepiratebay.org",
            "title": torrent["name"],
            "magnet": generate_magnet_link(torrent["info_hash"]),
            "size": convert_bytes(int(torrent["size"])),
            "views": None,
            "seeders": int(torrent["seeders"]),
            "leechers": int(torrent["leechers"])
        })

    return results
