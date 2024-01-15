import _config as config
from src import helpers
from urllib.parse import quote
from flask import request


def get_catagory_code(cat):
    if cat == "xxx" and request.cookie.get("safe", "active") != "active":
        return "500"

    catagory_codes = {
        'all': '',
        'audiobook': '102',
        'movie': '201',
        'tv': '205',
        'games': '400',
        'software': '300',
        'music': '100'
    }

    return catagory_codes.get(cat)


def search(query, catagory, results_object):
    if "tpb" not in config.ENABLED_TORRENT_SITES:
        return []

    catagory = get_catagory_code(catagory)
    if catagory is None:
        return []

    url = f"https://{config.API_BAY_DOMAIN}/q.php?q={quote(query)}&cat={catagory}"
    try:
        torrent_data = helpers.makeJSONRequest(
            url,
            timeout=8,
        )
    except:
        return
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
            "seeders": int(torrent["seeders"]),
            "leechers": int(torrent["leechers"]),
            "post_link": f"https://thepiratebay.org/{torrent['id']}"
        })

    results_object.extend(results)
