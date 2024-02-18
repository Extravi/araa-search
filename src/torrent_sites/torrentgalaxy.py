from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "torrentgalaxy"

def get_catagory_code(cat):
    match cat:
        case "all":
            return ""
        case "audiobook":
            return "&c13=1"
        case "movie":
            return "&c3=1&c46=1&c45=1&c42=1&c4=1&c1=1" 
        case "tv":
            return "&c41=1&c5=1&c11=1&c6=1&c7=1"
        case "games":
            return "&c43=1&c10=1"
        case "software":
            return "&c20=1&c21=1&c18=1"
        case "anime":
            return "&c28=1"
        case "music":
            return "&c28=1&c22=1&c26=1&c23=1&c25=1&c24=1"
        case "xxx":
            safesearch = (request.cookies.get("safe", "active") == "active")
            if safesearch:
                return "ignore"
            return "&c48=1&c35=1&c47=1&c34=1"
        case _:
            return ""


def search(query, catagory="all"):
    catagory = get_catagory_code(catagory)
    if catagory == "ignore":
        return []
    soup = helpers.makeHTMLRequest(f"https://{TORRENTGALAXY_DOMAIN}/torrents.php?search={quote(query)}{catagory}#results")

    result_divs = soup.findAll("div", {"class": "tgxtablerow"})
    title = [div.find("div", {"id": "click"}) for div in result_divs]
    title = [title.text.strip() for title in title]
    magnet_links = [
        div.find("a", href=lambda href: href and href.startswith("magnet")).get("href")
        for div in result_divs
    ]
    byte_sizes = [
        helpers.string_to_bytes(div.find("span", {"class": "badge-secondary"}).text.strip())
        for div in result_divs
    ]
    view_counts = [int(div.find("font", {"color": "orange"}).text.replace(',', '')) for div in result_divs]
    seeders = [int(div.find("font", {"color": "green"}).text.replace(',', '')) for div in result_divs]
    leechers = [int(div.find("font", {"color": "#ff0000"}).text.replace(',', '')) for div in result_divs]

    # list
    results = []
    for title, magnet_link, byte_size, view_count, seeder, leecher in zip(
        title, magnet_links, byte_sizes, view_counts, seeders, leechers):
        results.append({
            "href": TORRENTGALAXY_DOMAIN,
            "title": title,
            "magnet": helpers.apply_trackers(magnet_link),
            "bytes": byte_size,
            "size": helpers.bytes_to_string(byte_size),
            "views": view_count,
            "seeders": seeder,
            "leechers": leecher
        })

    return results
