from _config import *
from src import helpers
from urllib.parse import quote

def name():
    return "torrentgalaxy"

def search(query):
    soup = helpers.makeHTMLRequest(f"https://{TORRENTGALAXY_DOMAIN}/torrents.php?search={quote(query)}#results")

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
