import time
from src.helpers import latest_commit
from _config import *
from flask import request, render_template, jsonify, Response
from src.torrent_sites import torrentgalaxy, nyaa


def torrentResults(query) -> Response:
    if not TORRENTSEARCH_ENABLED:
        return jsonify({"error": "Torrent search disabled by instance operator"}), 503

    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")
    query = request.args.get("q", " ").strip()

    sites = [
        torrentgalaxy.torrentgalaxy,
        nyaa.nyaa
    ]

    results = []
    for site in sites:
        results += site(query)

    # Sorts based on how many seeders there are on a torrent.
    results = sorted(results, key=lambda x: x["seeders"])[::-1]


    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    if api == "true" and API_ENABLED:
        # return the results list as a JSON response
        return jsonify(results)

    return render_template("torrents.html",
                        results=results, title=f"{query} - TailsX",
                        q=f"{query}", fetched=f"Fetched the results in {elapsed_time:.2f} seconds",
                        theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
                        javascript=request.cookies.get('javascript', 'enabled'), type="torrent",
                        repo_url=REPO, API_ENABLED=API_ENABLED, TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED,
                        commit=latest_commit()
                        )
