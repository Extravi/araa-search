import _config as config
from src import helpers
from urllib.parse import quote
from flask import request


def get_magnet_anchor(anchors: list):
    for anchor in anchors:
        if "magnet" in anchor:
            return anchor


def get_catagory_code(cat):
    if cat == "xxx" and request.cookie.get("safe", "active") != "active":
        return "&c48=1&c35=1&c47=1&c34=1"

    catagory_codes = {
        'all': '',
        'audiobook': '&c13=1',
        'movie': '&c3=1&c46=1&c45=1&c42=1&c4=1&c1=1',
        'tv': '&c41=1&c5=1&c11=1&c6=1&c7=1',
        'games': '&c43=1&c10=1',
        'software': '&c20=1&c21=1&c18=1',
        'anime': '&c28=1',
        'music': '&c28=1&c22=1&c26=1&c23=1&c25=1&c24=1'
    }

    return catagory_codes.get(cat)


def search(query, catagory, results_object):
    if "torrentgalaxy" not in config.ENABLED_TORRENT_SITES:
        return []

    catagory = get_catagory_code(catagory)
    if catagory is None:
        return []

    try:
        soup = helpers.makeHTMLRequest(
            f"https://{config.TORRENTGALAXY_DOMAIN}/torrents.php?search={quote(query)}{catagory}#results",
            timeout=8,
        )
    except:
        return []

    results = []
    for result in soup.findAll("div", {"class": "tgxtablerow"}):
        list_of_anchors = result.find_all("a")
        byte_size = result.find("span", {"class": "badge-secondary"}).get_text()
        list_of_bolds = result.find_all("b")
        magnet = get_magnet_anchor(list_of_anchors)
        if magnet is None:
            continue

        results.append({
            "href": config.TORRENTGALAXY_DOMAIN,
            "title": list_of_anchors[1].get_text(),
            "post_link": f"https://{config.TORRENTGALAXY_DOMAIN}{list_of_anchors[1].get('href')}",
            "magnet": helpers.apply_trackers(magnet),
            "bytes": byte_size,
            "size": helpers.bytes_to_string(byte_size),
            "seeders": int(list_of_bolds[2].replace(',', '')),
            "leechers": int(list_of_bolds[3].replace(',', '')),
        })

    results_object.extend(results)
