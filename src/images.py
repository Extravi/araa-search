from src.helpers import makeHTMLRequest, latest_commit
from urllib.parse import unquote, quote
from _config import *
from flask import request, render_template, jsonify, Response, redirect
import time
import json
from urllib.parse import quote
import base64


def imageResults(query) -> Response:
    # get user language settings
    ux_lang = request.cookies.get('ux_lang', 'english')
    json_path = f'static/lang/{ux_lang}.json'
    with open(json_path, 'r') as file:
        lang_data = json.load(file)

    # remember time we started
    start_time = time.time()

    api = request.args.get("api", "false")

    p = request.args.get('p', '1')
    if not p.isdigit():
        return redirect('/search')

    # returns 1 if active, else 0
    safe_search = int(request.cookies.get("safe", "active") == "active")

    # grab & format webpage
    soup = makeHTMLRequest(f"https://lite.qwant.com/?q={quote(query)}&t=images&p={p}&s={safe_search}")

    try:
        # get 'img' ellements
        ellements = soup.findAll("div", {"class": "images-container"})
        # get source urls
        image_sources = [a.find('img')['src'] for a in ellements[0].findAll('a') if a.find('img')]
    except:
        return redirect('/search')

    # get alt tags
    image_alts = [img['alt'] for img in ellements[0].findAll('img', alt=True)]

    # generate results
    images = [f"/img_proxy?url={quote(img_src)}" for img_src in image_sources]

    # decode urls
    links = [a['href'] for a in ellements[0].findAll('a') if a.has_attr('href')]
    links = [url.split("?position")[0].split("==/")[-1] for url in links]
    links = [unquote(base64.b64decode(link).decode('utf-8')) for link in links]

    # list
    results = []
    for image, link, image_alt in zip(images, links, image_alts):
        results.append((image, link, image_alt))

    # calc. time spent
    end_time = time.time()
    elapsed_time = end_time - start_time

    # render
    if api == "true" and API_ENABLED == True:
        # return the results list as a JSON response
        return jsonify(results)
    else:
        return render_template("images.html", results=results, title=f"{query} - Araa",
            q=f"{query}", fetched=f"{elapsed_time:.2f}",
            theme=request.cookies.get('theme', DEFAULT_THEME), DEFAULT_THEME=DEFAULT_THEME,
            javascript=request.cookies.get('javascript', 'enabled'), type="image",
            new_tab=request.cookies.get("new_tab"), repo_url=REPO, API_ENABLED=API_ENABLED,
            TORRENTSEARCH_ENABLED=TORRENTSEARCH_ENABLED, ux_lang=ux_lang, lang_data=lang_data,
            commit=latest_commit())
