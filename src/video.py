from src.helpers import makeHTMLRequest
from _config import *
from flask import request, render_template, jsonify, Response
import time
import json
from src.helpers import latest_commit


def videoResults(query) -> Response:
    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")

    # grab & format webpage
    soup = makeHTMLRequest(f"https://{INVIDIOUS_INSTANCE}/api/v1/search?q={query}")
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
    publisher_text = ["YouTube" for creator in videos]

    # retrieve images
    video_thumbnails = [item['videoThumbnails'] for item in data if item.get('type') == 'video']
    maxres_thumbnails = [thumbnail for thumbnails in video_thumbnails for thumbnail in thumbnails if thumbnail['quality'] == 'medium']
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

    if api == "true":
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("videos.html",
                               results=results, title=f"{query} - TailsX",
                               q=f"{query}", fetched=f"Fetched the results in {elapsed_time:.2f} seconds",
                               theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
                               javascript=request.cookies.get('javascript', 'enabled'), new_tab=request.cookies.get("new_tab"),
                               type="video", repo_url=REPO, commit=latest_commit()
                               )
