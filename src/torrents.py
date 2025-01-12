import time
import json
from src import helpers
from _config import *
from flask import request, render_template, jsonify, Response
from src.torrent_sites import torrentgalaxy, nyaa, thepiratebay, rutor

def torrentResults(query) -> Response:
    settings = helpers.Settings()

    if not TORRENTSEARCH_ENABLED:
        return jsonify({"error": "Torrent search disabled by instance operator"}), 503

    # Define where to get request args from. If the request is using GET,
    # use request.args. Otherwise (POST), use request.form
    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    # get user language settings
    json_path = f'static/lang/{settings.ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = helpers.format_araa_name(json.load(file))

    # remember time we started
    start_time = time.time()

    api = args.get("api", "false")
    catagory = args.get("cat", "all")
    query = args.get("q", " ").strip()
    sort = args.get("sort", "seed")
    if sort not in ["seed", "leech", "lth", "htl"]:
        sort = "seed"

    sites = [
        torrentgalaxy,
        nyaa,
        thepiratebay,
        rutor,
    ]

    results = []
    for site in sites:
        if site.name() in ENABLED_TORRENT_SITES:
            try:
                # For some reason, rutor doesn't give reliable catagories.
                if catagory != "all" and site.name() == "rutor":
                    continue
                results += site.search(query, catagory=catagory)
            except:
                continue

    # Allow user to decide how the results are sorted
    match sort:
        case "leech":
            results = sorted(results, key=lambda x: x["leechers"])[::-1]
        case "lth": # Low to High file size
            results = sorted(results, key=lambda x: x["bytes"])
        case "htl": # High to low file size
            results = sorted(results, key=lambda x: x["bytes"])[::-1]
        case _: # Defaults to seeders
            results = sorted(results, key=lambda x: x["seeders"])[::-1]


    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    if api == "true" and API_ENABLED:
        # return the results list as a JSON response
        return jsonify(results)

    return render_template("torrents.html",
                        results=results, title=f"{query} - {ARAA_NAME}",
                        q=f"{query}", fetched=f"{elapsed_time:.2f}",
                        cat=catagory, type="torrent", repo_url=REPO, donate_url=DONATE,
                        API_ENABLED=API_ENABLED, TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED,
                        lang_data=lang_data, commit=helpers.latest_commit(), sort=sort, settings=settings,
                        araa_name=ARAA_NAME
                        )
