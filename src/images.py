from src import helpers
from urllib.parse import quote, urlparse
from _config import *
from flask import request, render_template, jsonify, Response, redirect
import time
import requests
import os
import re

IMAGE_ENGINES = [
    {"name": "google", "display": "Google"},
    {"name": "qwant", "display": "Qwant"},
]

IMAGE_ENGINE_NAME_MAP = {
    "google": "google images",
    "qwant": "qwant images",
}


def _safe_int(value, fallback=1):
    try:
        return int(value)
    except Exception:
        return fallback


def _local_searxng_base_url():
    # Prefer the URL exposed by startup bootstrap logic.
    base_url = os.environ.get("ARAA_LOCAL_SEARXNG_URL", "").strip()
    if base_url != "":
        return base_url.rstrip("/")

    # Fallback to static config if the bootstrap did not set env vars.
    return f"http://{LOCAL_SEARXNG_HOST}:{LOCAL_SEARXNG_PORT}"


def _parse_resolution(raw_resolution):
    match = re.search(r'(\d+)\s*[xX]\s*(\d+)', raw_resolution)
    if match is None:
        return (0, 0)
    return (_safe_int(match.group(1), 0), _safe_int(match.group(2), 0))


def _normalize_image_engine(name: str) -> str:
    name = (name or "").strip().lower()
    if name in IMAGE_ENGINE_NAME_MAP:
        return name
    return "google"


def imageResults(query) -> Response:
    # get user language settings
    settings = helpers.Settings()

    if request.method == "GET":
        args = request.args
    else:
        args = request.form

    lang_data = helpers.load_lang_data(settings.ux_lang)

    # remember time we started
    start_time = time.time()

    api = args.get("api", "false")
    after_date = args.get("after", "")
    before_date = args.get("before", "")

    p_raw = args.get('p', '1')
    if not p_raw.isdigit():
        return redirect('/search')
    p = _safe_int(p_raw, 1)
    if p < 1:
        p = 1

    image_engine = _normalize_image_engine(settings.image_engine)
    settings.image_engine = image_engine

    # searxng uses 0, 1, 2 for safesearch levels.
    safe_search = 2 if settings.safe == "active" else 0

    # Append optional date filters when provided.
    query_for_engine = query
    if after_date != "":
        query_for_engine += f" after:{after_date}"
    if before_date != "":
        query_for_engine += f" before:{before_date}"

    # Query local searxng image engines.
    link_args = {
        "q": query_for_engine,
        "format": "json",
        "engines": IMAGE_ENGINE_NAME_MAP[image_engine],
        "categories": "images",
        "safesearch": safe_search,
        "pageno": p,
    }

    searx_lang = helpers.settings_lang_to_searx(settings.lang)
    if searx_lang != "":
        link_args["language"] = searx_lang

    link = f"{_local_searxng_base_url()}/search"

    try:
        response = requests.get(link, params=link_args, timeout=45)
    except Exception as e:
        print(f"WARN: Local searxng image request failed: {e}")
        response = None

    if response is None or response.status_code != 200:
        if response is not None:
            print(f"WARN: Image engine returned status {response.status_code} for query={query}")
        images = []
    else:
        try:
            json_data = response.json()
        except Exception as e:
            print(f"WARN: Failed to parse image engine response JSON: {e}")
            images = []
        else:
            if not isinstance(json_data, dict):
                images = []
            else:
                images = json_data.get("results", [])
                if not isinstance(images, list):
                    images = []

    results = []
    for image in images:
        if not isinstance(image, dict):
            continue

        # Ensure thumbnail and full image links are present for the image viewer.
        thumb_src = str(image.get("thumbnail_src") or image.get("thumbnail") or image.get("img_src") or "").strip()
        media_src = str(image.get("img_src") or "").strip()
        href = str(image.get("url") or "").strip()

        if thumb_src == "":
            continue
        if media_src == "":
            media_src = thumb_src
        if href == "":
            href = media_src

        width, height = _parse_resolution(str(image.get("resolution", "")))
        source_domain = urlparse(href).netloc

        results.append({
            "url": href,
            "title": str(image.get("title", "")).strip(),
            "source": source_domain,
            "media": media_src,
            "thumb_proxy": f"/img_proxy?url={quote(thumb_src)}",
            "width": width,
            "height": height,
            "thumb_height": height,
        })

    if len(results) <= 0:
        # Render the images page with no results instead of redirecting
        # to /search. This provides a friendlier error path for users
        # when no image engine is available.
        elapsed_time = time.time() - start_time
        if api == "true" and API_ENABLED:
            return jsonify([])
        return render_template("images.html", results=None, title=f"{query} - {ARAA_NAME}",
            q=f"{query}", fetched=f"{elapsed_time:.2f}", type="image",
            repo_url=REPO, donate_url=DONATE, API_ENABLED=API_ENABLED,
            TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, lang_data=lang_data,
            commit=helpers.latest_commit(), settings=settings, araa_name=ARAA_NAME,
            image_engine_display=IMAGE_ENGINE_NAME_MAP[image_engine],
            available_image_engines=IMAGE_ENGINES,
            before=before_date, after=after_date,
            current_url=request.url)

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    # render
    if api == "true" and API_ENABLED:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("images.html", results=results, title=f"{query} - {ARAA_NAME}",
            q=f"{query}", fetched=f"{elapsed_time:.2f}",
            type="image",
            repo_url=REPO, donate_url=DONATE, API_ENABLED=API_ENABLED,
            TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, lang_data=lang_data,
            commit=helpers.latest_commit(), settings=settings, araa_name=ARAA_NAME,
            image_engine_display=IMAGE_ENGINE_NAME_MAP[image_engine],
            available_image_engines=IMAGE_ENGINES,
            before=before_date, after=after_date,
            current_url=request.url)
