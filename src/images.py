from src import helpers
from urllib.parse import unquote, quote
from _config import *
from flask import request, render_template, jsonify, Response, redirect
import time
import json
from urllib.parse import quote
import requests
import random


def imageResults(query) -> Response:
    # get user language settings
    settings = helpers.Settings()

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

    p = args.get('p', '1')
    if not p.isdigit():
        return redirect('/search')

    # returns 1 if active, else 0
    safe_search = int(settings.safe == "active")

    # grab & format webpage
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    response = requests.get(f"https://api.qwant.com/v3/search/images?t=images&q={quote(query)}&count=50&locale=en_CA&offset={p}&device=desktop&tgp=2&safesearch={safe_search}", headers=headers)
    json_data = response.json()

    try:
        # get 'img' ellements
        elements = json_data["data"]["result"]["items"]
        # get source urls
        image_sources = [item["media_preview"] for item in elements]
        media_fullsize = [item["media_fullsize"] for item in elements]
        media_fullsize_no_proxy = [item["media"] for item in elements]
    except:
        return redirect('/search')

    # get alt tags
    image_alts = [item["title"] for item in elements]

    # generate results
    images = [f"/img_proxy?url={quote(img_src)}" for img_src in image_sources]
    media_fullsize_images = [f"/img_proxy?url={quote(img_src)}" for img_src in media_fullsize]
    media_fullsize_images_no_proxy = [img_src for img_src in media_fullsize_no_proxy]

    # source urls
    links = [item["url"] for item in elements]

    # list
    results = []
    for image, link, image_alt, image_fullsize, image_fullsize_no_proxy in zip(images, links, image_alts, media_fullsize_images, media_fullsize_images_no_proxy):
        results.append((image, link, image_alt, image_fullsize, image_fullsize_no_proxy))

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    # render
    if api == "true" and API_ENABLED:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("images.html", results=results, title=f"{query} - Araa",
            q=f"{query}", fetched=f"{elapsed_time:.2f}",
            type="image",
            repo_url=REPO, donate_url=DONATE, API_ENABLED=API_ENABLED,
            TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, lang_data=lang_data,
            commit=helpers.latest_commit(), settings=settings)
