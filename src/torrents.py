from src.helpers import makeHTMLRequest, latest_commit
from _config import *
from flask import request, render_template, jsonify, Response
import time


def torrentResults(query) -> Response:
    if TORRENTSEARCH_ENABLED == False:
        return jsonify({"error": "Torrent search disabled by instance operator"}), 503
    else:

        # remember time we started
        start_time = time.time()

        api = request.args.get("api", "false")

        # grab & format webpage
        soup = makeHTMLRequest(f"https://{TORRENTGALAXY_DOMAIN}/torrents.php?search={query}#results")

        result_divs = soup.findAll("div", {"class": "tgxtablerow"})
        title = [div.find("div", {"id": "click"}) for div in result_divs]
        title = [title.text.strip() for title in title]
        hrefs = ["torrentgalaxy.to" for title in title]
        magnet_links = [div.find("a", href=lambda href: href and href.startswith("magnet")).get("href") for div in result_divs]
        file_sizes = [div.find("span", {"class": "badge-secondary"}).text.strip() for div in result_divs]
        view_counts = [div.find("font", {"color": "orange"}).text.strip() for div in result_divs]
        seeders = [div.find("font", {"color": "green"}).text.strip() for div in result_divs]
        leechers = [div.find("font", {"color": "#ff0000"}).text.strip() for div in result_divs]

        # list
        results = []
        for href, title, magnet_link, file_size, view_count, seeder, leecher in zip(hrefs, title, magnet_links, file_sizes, view_counts, seeders, leechers):
            results.append([href, title, magnet_link, file_size, view_count, seeder, leecher])

        # calc. time spent
        end_time = time.time()
        elapsed_time = end_time - start_time

        if api == "true" and API_ENABLED == True:
            # return the results list as a JSON response
            return jsonify(results)
        else:
            return render_template("torrents.html",
                                results=results, title=f"{query} - TailsX",
                                q=f"{query}", fetched=f"Fetched the results in {elapsed_time:.2f} seconds",
                                theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
                                javascript=request.cookies.get('javascript', 'enabled'), type="torrent",
                                repo_url=REPO, API_ENABLED=API_ENABLED, TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED,
                                commit=latest_commit()
                                )
