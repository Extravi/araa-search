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


def videoResults(query) -> Response:
    settings = helpers.Settings()

    # Define where to get request args from. If the request is using GET,
    # use request.args. Otherwise (POST), use request.form
    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    json_path = f'static/lang/{settings.ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    api = args.get("api", "false")

    # grab & format webpage
    soup, response_code = makeHTMLRequest(f"https://{PIPED_INSTANCE_API}/search?q={quote(query)}&filter=all", is_piped=True)
    data = json.loads(soup.text)

    # retrieve links
    ytIds = [item["url"] for item in data["items"] if item.get("type") not in ["channel", "playlist"]]
    hrefs = [f"https://{PIPED_INSTANCE}{ytId}" for ytId in ytIds]

    # retrieve title
    title = [item["title"] for item in data["items"] if item.get("type") not in ["channel", "playlist"]]

    # retrieve date
    date_span = [item["uploadedDate"] for item in data["items"] if item.get("type") not in ["channel", "playlist"]]

    # retrieve views
    views = [f"{views//1000000000}B views" if views >= 1000000000 else f"{views//1000000}M views" if views >= 1000000 else f"{views/1000:.1f}K views" if 1000 < views < 10000 else f"{views//1000}K views" if views >= 10000 else f"{views} views" for views in [item["views"] for item in data["items"] if item.get("type") not in ["channel", "playlist"]]]

    # retrieve creator
    creator_text = [item["uploaderName"] for item in data["items"] if item.get("type") not in ["channel", "playlist"]]

    # retrieve publisher
    publisher_text = ["Piped" for item in data["items"] if item.get("type") not in ["channel", "playlist"]]

    # retrieve images
    filtered_urls = [item["thumbnail"] for item in data["items"] if item.get("type") not in ["channel", "playlist"]]
    filtered_urls = [f'/img_proxy?url={filtered_url}' for filtered_url in filtered_urls]

    # retrieve time
    duration = [item["duration"] for item in data["items"] if item.get("type") not in ["channel", "playlist"]]
    formatted_durations = [parse_time(duration) for duration in duration]

    # list
    results = []
    for href, title, date, view, creator, publisher, image, duration in zip(hrefs, title, date_span, views, creator_text, publisher_text, filtered_urls, formatted_durations):
        results.append([href, title, date, view, creator, publisher, image, duration])

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    if api == "true" and API_ENABLED == True:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("videos.html",
                               results=results, title=f"{query} - Araa",
                               q=f"{query}", fetched=f"{elapsed_time:.2f}",
                               type="video", repo_url=REPO, donate_url=DONATE, API_ENABLED=API_ENABLED, TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED,
                               lang_data=lang_data, commit=latest_commit(), settings=settings
                               )
