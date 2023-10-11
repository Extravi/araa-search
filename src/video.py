from src.helpers import makeHTMLRequest
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json
from src.helpers import latest_commit
from urllib.parse import quote

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours != 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def videoResults(query, api=False) -> Response:
    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    # grab & format webpage
    soup = makeHTMLRequest(f"https://{INVIDIOUS_INSTANCE}/api/v1/search?q={quote(query)}")
    data = json.loads(soup.text)

    results = []
    for video in data:
        if video["type"] != "video":
            continue
        for thumbnail in video['videoThumbnails']:
            if thumbnail["quality"] == "medium":
                thumbnail_link = '/img_proxy?url=' + thumbnail['url']
        results.append({
            "publisher": "YouTube",
            "title": video["title"],
            "link": f"https://{INVIDIOUS_INSTANCE}/watch?v={video['videoId']}",
            "views": video["viewCountText"],
            "date_span": video["publishedText"],
            "author": video["author"],
            "length": format_duration(video["lengthSeconds"]),
            "thumbnail": thumbnail_link
        })

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    if api and API_ENABLED:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("videos.html",
                               results=results, title=f"{query} - Araa",
                               q=f"{query}", fetched=f"{elapsed_time:.2f}",
                               theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
                               javascript=request.cookies.get('javascript', 'enabled'), new_tab=request.cookies.get("new_tab"),
                               type="video", repo_url=REPO, API_ENABLED=API_ENABLED, TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, ux_lang=ux_lang, 
                               lang_data=lang_data, commit=latest_commit()
                               )
