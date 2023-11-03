import time
import json
from src.helpers import latest_commit
from _config import *
from flask import request, render_template, jsonify, Response
from src.torrent_sites import torrentgalaxy, nyaa, thepiratebay, rutor

def torrentResults(query) -> Response:
    if not TORRENTSEARCH_ENABLED:
        return jsonify({"error": "Torrent search disabled by instance operator"}), 503

    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")
    catagory = request.args.get("cat", "all")
    query = request.args.get("q", " ").strip()
    safesearch = request.cookies.get("safe", "active")
    sort = request.args.get("sort", "seed")
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
        case "htl": # Low to High file size
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
                        results=results, title=f"{query} - Araa",
                        q=f"{query}", fetched=f"{elapsed_time:.2f}",
                        cat=catagory, safesearch=safesearch,
                        theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
                        javascript=request.cookies.get('javascript', 'enabled'), type="torrent",
                        repo_url=REPO, API_ENABLED=API_ENABLED, TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED,
                        ux_lang=ux_lang, lang_data=lang_data,
                        commit=latest_commit(), sort=sort
                        )
