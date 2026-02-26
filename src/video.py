from src.helpers import makeHTMLRequest
from src import helpers
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json
from src.helpers import latest_commit
from urllib.parse import quote


def parse_time(time):
    hours = time // 3600
    minutes = (time % 3600) // 60
    seconds = time % 60
    time_string = ""
    if hours != 0:
        time_string += f"{hours:02d}:"
    return f"{time_string}{minutes:02d}:{seconds:02d}"


def parse_views(views):
    if views >= 1000000000:
        return f"{views//1000000000}B views"
    if views >= 1000000:
        return f"{views//1000000}M views"
    if 1000 < views < 10000:
        return f"{views/1000:.1f}K views"
    if views >= 10000:
        return f"{views//1000}K views"
    return f"{views} views"


def render_results(query: str, settings, lang_data, results: list, elapsed_time: float, api: str) -> Response:
    if api == "true" and API_ENABLED == True:
        # return the results list as a JSON response
        return jsonify(results)

    return render_template("videos.html",
                           results=results, title=f"{query} - {ARAA_NAME}",
                           q=f"{query}", fetched=f"{elapsed_time:.2f}",
                           type="video", repo_url=REPO, donate_url=DONATE, API_ENABLED=API_ENABLED, TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED,
                           lang_data=lang_data, commit=latest_commit(), settings=settings, araa_name=ARAA_NAME
                           )


def videoResults(query) -> Response:
    settings = helpers.Settings()

    # Define where to get request args from. If the request is using GET,
    # use request.args. Otherwise (POST), use request.form
    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    lang_data = helpers.load_lang_data(settings.ux_lang)

    # remember time we started
    start_time = time.time()

    api = args.get("api", "false")
    results = []

    try:
        # grab & format webpage
        soup, response_code = makeHTMLRequest(f"https://{PIPED_INSTANCE_API}/search?q={quote(query)}&filter=all", is_piped=True)
    except Exception as e:
        print(f"WARN: Video request failed: {e}")
        soup, response_code = (None, 0)

    if soup is None or response_code != 200:
        if response_code != 0:
            print(f"WARN: Video engine returned status {response_code} for query={query}")
        elapsed_time = time.time() - start_time
        return render_results(query, settings, lang_data, results, elapsed_time, api)

    try:
        data = json.loads(soup.text)
    except Exception as e:
        print(f"WARN: Failed to parse video engine response JSON: {e}")
        elapsed_time = time.time() - start_time
        return render_results(query, settings, lang_data, results, elapsed_time, api)

    if not isinstance(data, dict):
        elapsed_time = time.time() - start_time
        return render_results(query, settings, lang_data, results, elapsed_time, api)

    items = data.get("items", [])
    if not isinstance(items, list):
        items = []

    # list
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("type") in ["channel", "playlist"]:
            continue

        yt_id = str(item.get("url", "")).strip()
        title = str(item.get("title", "")).strip()
        uploaded_date = str(item.get("uploadedDate", "")).strip()
        uploader_name = str(item.get("uploaderName", "")).strip()
        thumbnail = str(item.get("thumbnail", "")).strip()

        try:
            views = int(item.get("views", 0))
        except Exception:
            views = 0

        try:
            duration = int(item.get("duration", 0))
        except Exception:
            duration = 0

        if yt_id == "" or title == "":
            continue
        if thumbnail == "":
            continue

        results.append([
            f"https://{PIPED_INSTANCE}{yt_id}",
            title,
            uploaded_date,
            parse_views(views),
            uploader_name,
            "Piped",
            f"/img_proxy?url={quote(thumbnail)}",
            parse_time(max(duration, 0))
        ])

    # calc. time spent
    elapsed_time = time.time() - start_time
    return render_results(query, settings, lang_data, results, elapsed_time, api)
