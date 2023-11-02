from src.helpers import makeHTMLRequest
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json
from src.helpers import latest_commit
from urllib.parse import quote


def videoResults(query) -> Response:
    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")

    # grab & format webpage
    soup = makeHTMLRequest(f"https://{INVIDIOUS_INSTANCE}/api/v1/search?q={quote(query)}")
    data = json.loads(soup.text)

    # sort by videos only
    videos = [item for item in data if item.get("type") == "video"]

    # retrieve links
    ytIds = [video["videoId"] for video in videos]
    hrefs = [f"https://{INVIDIOUS_INSTANCE}/watch?v={ytId}" for ytId in ytIds]

    # retrieve title
    title = [title["title"] for title in videos]

    # retrieve date
    date_span = [date["publishedText"] for date in videos]

    # retrieve views
    views = [views["viewCountText"] for views in videos]

    # retrieve creator
    creator_text = [creator_text["author"] for creator_text in videos]

    # retrieve publisher
    publisher_text = ["Invidious" for creator in videos]

    # retrieve images
    video_thumbnails = [item['videoThumbnails'] for item in data if item.get('type') == 'video']
    maxres_thumbnails = [thumbnail for thumbnails in video_thumbnails for thumbnail in thumbnails if thumbnail['quality'] == 'medium']

    #For some reason, URLs aren't standardized across different instances of Invidious' API, some instances use relative URLs. This is a quick workaround.
    if INVIDIOUS_INSTANCE not in maxres_thumbnails[0]["url"]:
        filtered_urls = ['/img_proxy?url=https://' + INVIDIOUS_INSTANCE + thumbnail['url'].replace(":3000", "").replace("http://", "https://") for thumbnail in maxres_thumbnails]
    else: 
        filtered_urls = ['/img_proxy?url=' + thumbnail['url'].replace(":3000", "").replace("http://", "https://") for thumbnail in maxres_thumbnails]


    # retrieve time
    duration = [duration["lengthSeconds"] for duration in videos]
    formatted_durations = [f"{duration // 60:02d}:{duration % 60:02d}" for duration in duration]

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
                               theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
                               javascript=request.cookies.get('javascript', 'enabled'), new_tab=request.cookies.get("new_tab"),
                               type="video", repo_url=REPO, API_ENABLED=API_ENABLED, TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, ux_lang=ux_lang, 
                               lang_data=lang_data, commit=latest_commit()
                               )
