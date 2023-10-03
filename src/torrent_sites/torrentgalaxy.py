from _config import *
from src import helpers

def name():
    return "torrentgalaxy"

def search(query):
    soup = helpers.makeHTMLRequest(f"https://{TORRENTGALAXY_DOMAIN}/torrents.php?search={query}#results")

    result_divs = soup.findAll("div", {"class": "tgxtablerow"})
    title = [div.find("div", {"id": "click"}) for div in result_divs]
    title = [title.text.strip() for title in title]
    hrefs = [TORRENTGALAXY_DOMAIN for title in title]
    magnet_links = [
        div.find("a", href=lambda href: href and href.startswith("magnet")).get("href")
        for div in result_divs
    ]
    file_sizes = [
        div.find("span", {"class": "badge-secondary"}).text.strip()
        for div in result_divs
    ]
    view_counts = [int(div.find("font", {"color": "orange"}).text.replace(',', '')) for div in result_divs]
    seeders = [int(div.find("font", {"color": "green"}).text.replace(',', '')) for div in result_divs]
    leechers = [int(div.find("font", {"color": "#ff0000"}).text.replace(',', '')) for div in result_divs]

    # list
    results = []
    for href, title, magnet_link, file_size, view_count, seeder, leecher in zip(
        hrefs, title, magnet_links, file_sizes, view_counts, seeders, leechers):
        results.append({
            "href": href,
            "title": title,
            "magnet": magnet_link,
            "size": file_size,
            "views": view_count,
            "seeders": seeder,
            "leechers": leecher
        })

    return results
