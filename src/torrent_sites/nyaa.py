import _config as config
from src import helpers
from urllib.parse import quote


def get_catagory_code(cat):
    catagory_codes = {
        "all": "",
        "anime": "&c=1_0",
        "music": "&c=2_0",
        "game": "&c=6_2",
        "software": "&c=6_1"
    }
    return catagory_codes.get(cat)


def search(query, catagory, results_object):
    if "nyaa" not in config.ENABLED_TORRENT_SITES:
        return []

    catagory = get_catagory_code(catagory)
    if catagory is None:
        return []

    try:
        soup = helpers.makeHTMLRequest(
            f"https://{config.NYAA_DOMAIN}/?f=0&q={quote(query)}{catagory}",
            timeout=8,
        )
    except:
        return

    results = []
    for torrent in soup.select(".default, .success, .danger"):
        list_of_tds = torrent.find_all("td")
        byte_size = helpers.string_to_bytes(list_of_tds[3].get_text().strip())
        title = list_of_tds[1].find_all("a")[-1]

        results.append({
            "href": config.NYAA_DOMAIN,
            "title": title.get_text(),
            "magnet": helpers.apply_trackers(list_of_tds[2].find_all("a")[-1]["href"]),
            "bytes": byte_size,
            "size": helpers.bytes_to_string(byte_size),
            "seeders": int(list_of_tds[5].get_text().strip()),
            "leechers": int(list_of_tds[6].get_text().strip()),
            "post_link": f"https://{config.NYAA_DOMAIN}{title['href']}"
        })

    results_object.extend(results)
